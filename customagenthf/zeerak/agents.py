"""Agent construction and feature execution for Zeerak."""

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass

from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel, ToolCallingAgent

from .config import (
    EXECUTION_STYLE_GUIDANCE,
    SEARCH_ENABLED_FEATURES,
    TOOL_CALLING_FEATURES,
    load_feature_prompt,
    model_fallback_id,
    model_id_for_feature,
)
from .formatting import OUTPUT_MODE_AUTO, format_feature_answer
from .policy import apply_rahnama_policy, apply_tabib_policy
from .routing import route_feature
from .schemas import (
    parse_education_response,
    parse_hunar_response,
    parse_rahnama_response,
    parse_tabib_response,
)


@dataclass(frozen=True)
class AgentAttempt:
    answer: str | None
    error: Exception | None
    stdout: str
    stderr: str


@dataclass(frozen=True)
class FeatureRunResult:
    requested_feature: str
    feature: str
    model: str
    raw_answer: str
    formatted_answer: str
    structured: dict[str, str] | None
    fallback_note: str | None = None
    route_reason: str | None = None


class ProviderAccessDeniedError(RuntimeError):
    """Raised when a provider denies access to the selected model."""


class RateLimitError(RuntimeError):
    """Raised when the provider signals a rate-limit or quota error."""


class TransientNetworkError(RuntimeError):
    """Raised on transient network or service-unavailability errors."""


def _parse_structured_payload(feature: str, formatted_answer: str) -> dict[str, str] | None:
    if feature == "rahnama":
        return parse_rahnama_response(formatted_answer).__dict__
    if feature == "tabib":
        return parse_tabib_response(formatted_answer).__dict__
    if feature == "hunar":
        return parse_hunar_response(formatted_answer).__dict__
    if feature == "education":
        return parse_education_response(formatted_answer).__dict__
    return None


def build_agent(feature: str, prefer_tool_calling: bool = True, model_id: str | None = None):
    selected_model_id = model_id or model_id_for_feature(feature)
    model = InferenceClientModel(model_id=selected_model_id)

    if feature in SEARCH_ENABLED_FEATURES:
        tools = [DuckDuckGoSearchTool()]
    else:
        tools = []

    if prefer_tool_calling and feature in TOOL_CALLING_FEATURES:
        return ToolCallingAgent(tools=tools, model=model)

    return CodeAgent(tools=tools, model=model)


def assemble_feature_task(prompt: str, task: str) -> str:
    return (
        f"{prompt}\n\n"
        f"Execution style: {EXECUTION_STYLE_GUIDANCE}\n\n"
        f"User request: {task}"
    )


def _run_agent_attempt(feature: str, full_task: str, model_id: str, prefer_tool_calling: bool) -> AgentAttempt:
    agent = build_agent(feature, prefer_tool_calling=prefer_tool_calling, model_id=model_id)
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            answer = str(agent.run(full_task))
    except Exception as exc:
        return AgentAttempt(
            answer=None,
            error=exc,
            stdout=stdout_buffer.getvalue(),
            stderr=stderr_buffer.getvalue(),
        )

    return AgentAttempt(
        answer=answer,
        error=None,
        stdout=stdout_buffer.getvalue(),
        stderr=stderr_buffer.getvalue(),
    )


def _emit_attempt_output(attempt: AgentAttempt) -> None:
    if attempt.stdout:
        print(attempt.stdout, end="")
    if attempt.stderr:
        print(attempt.stderr, end="", file=sys.stderr)


def _should_emit_attempt_output(feature: str) -> bool:
    return feature != "rahnama"


RATE_LIMIT_ERROR_PATTERNS = ("429", "rate limit", "quota", "too many requests")
TRANSIENT_ERROR_PATTERNS = ("502", "503", "504", "service unavailable", "connection error", "timeout", "read timed out")


def _is_bad_request_error(error_text: str) -> bool:
    return "bad request" in error_text or "400" in error_text


def _is_provider_access_error(error_text: str) -> bool:
    return "403" in error_text or "forbidden" in error_text or "provider" in error_text


def _is_rate_limit_error(error_text: str) -> bool:
    return any(pattern in error_text for pattern in RATE_LIMIT_ERROR_PATTERNS)


def _is_transient_error(error_text: str) -> bool:
    return any(pattern in error_text for pattern in TRANSIENT_ERROR_PATTERNS)


def _run_with_model_retries(feature: str, full_task: str, model_id: str) -> str:
    preferred_attempt = _run_agent_attempt(feature, full_task, model_id, prefer_tool_calling=True)
    if preferred_attempt.error is None:
        if _should_emit_attempt_output(feature):
            _emit_attempt_output(preferred_attempt)
        return preferred_attempt.answer or ""

    preferred_error_text = str(preferred_attempt.error).lower()

    if _is_provider_access_error(preferred_error_text):
        raise ProviderAccessDeniedError(str(preferred_attempt.error)) from preferred_attempt.error

    if _is_rate_limit_error(preferred_error_text):
        raise RateLimitError(str(preferred_attempt.error)) from preferred_attempt.error

    if _is_transient_error(preferred_error_text):
        raise TransientNetworkError(str(preferred_attempt.error)) from preferred_attempt.error

    if _is_bad_request_error(preferred_error_text):
        fallback_attempt = _run_agent_attempt(feature, full_task, model_id, prefer_tool_calling=False)
        if fallback_attempt.error is None:
            if _should_emit_attempt_output(feature):
                _emit_attempt_output(fallback_attempt)
            return fallback_attempt.answer or ""

        if _should_emit_attempt_output(feature):
            _emit_attempt_output(fallback_attempt)
        raise fallback_attempt.error

    if _should_emit_attempt_output(feature):
        _emit_attempt_output(preferred_attempt)
    raise preferred_attempt.error


def run_feature_result(
    feature: str,
    task: str,
    max_width: int | None = None,
    output_mode: str = OUTPUT_MODE_AUTO,
) -> FeatureRunResult:
    requested_feature = feature
    route_reason: str | None = None

    if feature == "auto":
        feature, route_reason = route_feature(task)

    prompt = load_feature_prompt(feature)

    if feature == "tabib":
        emergency, tabib_payload = apply_tabib_policy(task)
        if emergency:
            return FeatureRunResult(
                requested_feature=requested_feature,
                feature=feature,
                model="policy-short-circuit",
                raw_answer=tabib_payload,
                formatted_answer=tabib_payload,
                structured=None,
                fallback_note=None,
                route_reason=route_reason,
            )
        prompt = f"{prompt} {tabib_payload}"

    if feature == "rahnama":
        prompt = f"{prompt} {apply_rahnama_policy(task)}"

    primary_model = model_id_for_feature(feature)
    full_task = assemble_feature_task(prompt, task)
    used_model = primary_model
    fallback_note: str | None = None

    try:
        answer = _run_with_model_retries(feature, full_task, primary_model)
    except (ProviderAccessDeniedError, RateLimitError, TransientNetworkError) as exc:
        used_model = model_fallback_id()
        if used_model == primary_model:
            raise RuntimeError(
                f"Provider denied access to model '{primary_model}', and no distinct fallback model is configured."
            ) from exc

        if isinstance(exc, RateLimitError):
            note_reason = f"Rate limit reached for {primary_model}."
        elif isinstance(exc, TransientNetworkError):
            note_reason = f"Transient network error for {primary_model}."
        else:
            note_reason = f"Provider denied access to {primary_model}."

        answer = _run_with_model_retries(feature, full_task, used_model)
        fallback_note = f"[fallback] {note_reason} Retried with {used_model}."

    formatted_answer = format_feature_answer(feature, answer, max_width=max_width, output_mode=output_mode)
    structured = _parse_structured_payload(feature, formatted_answer)

    return FeatureRunResult(
        requested_feature=requested_feature,
        feature=feature,
        model=used_model,
        raw_answer=answer,
        formatted_answer=formatted_answer,
        structured=structured,
        fallback_note=fallback_note,
        route_reason=route_reason,
    )


def run_feature(
    feature: str,
    task: str,
    max_width: int | None = None,
    output_mode: str = OUTPUT_MODE_AUTO,
) -> str:
    result = run_feature_result(feature, task, max_width=max_width, output_mode=output_mode)

    sections: list[str] = []
    if result.requested_feature == "auto" and result.route_reason:
        sections.append(f"[router] Selected feature: {result.feature}. {result.route_reason}")
    if result.fallback_note:
        sections.append(result.fallback_note)
    sections.append(f"[model] {result.model}")
    sections.append(result.formatted_answer)

    return "\n\n".join(sections)

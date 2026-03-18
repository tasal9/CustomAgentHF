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
from .formatting import format_feature_answer
from .policy import apply_rahnama_policy, apply_tabib_policy
from .routing import route_feature


@dataclass(frozen=True)
class AgentAttempt:
    answer: str | None
    error: Exception | None
    stdout: str
    stderr: str


class ProviderAccessDeniedError(RuntimeError):
    """Raised when a provider denies access to the selected model."""


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


def _is_bad_request_error(error_text: str) -> bool:
    return "bad request" in error_text or "400" in error_text


def _is_provider_access_error(error_text: str) -> bool:
    return "403" in error_text or "forbidden" in error_text or "provider" in error_text


def _run_with_model_retries(feature: str, full_task: str, model_id: str) -> str:
    preferred_attempt = _run_agent_attempt(feature, full_task, model_id, prefer_tool_calling=True)
    if preferred_attempt.error is None:
        if _should_emit_attempt_output(feature):
            _emit_attempt_output(preferred_attempt)
        return preferred_attempt.answer or ""

    preferred_error_text = str(preferred_attempt.error).lower()
    if _is_provider_access_error(preferred_error_text):
        raise ProviderAccessDeniedError(str(preferred_attempt.error)) from preferred_attempt.error

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


def run_feature(feature: str, task: str, max_width: int | None = None) -> str:
    if feature == "auto":
        selected_feature, reason = route_feature(task)
        answer = run_feature(selected_feature, task, max_width=max_width)
        return f"[router] Selected feature: {selected_feature}. {reason}\n\n{answer}"

    prompt = load_feature_prompt(feature)

    if feature == "tabib":
        emergency, tabib_payload = apply_tabib_policy(task)
        if emergency:
            return tabib_payload
        prompt = f"{prompt} {tabib_payload}"

    if feature == "rahnama":
        prompt = f"{prompt} {apply_rahnama_policy(task)}"

    primary_model = model_id_for_feature(feature)
    full_task = assemble_feature_task(prompt, task)
    used_model = primary_model
    fallback_note = ""

    try:
        answer = _run_with_model_retries(feature, full_task, primary_model)
    except ProviderAccessDeniedError:
        used_model = model_fallback_id()
        if used_model == primary_model:
            raise RuntimeError(
                f"Provider denied access to model '{primary_model}', and no distinct fallback model is configured."
            )

        answer = _run_with_model_retries(feature, full_task, used_model)
        fallback_note = f"[fallback] Provider denied access to {primary_model}. Retried with {used_model}.\n\n"

    formatted_answer = format_feature_answer(feature, answer, max_width=max_width)
    return f"{fallback_note}[model] {used_model}\n\n{formatted_answer}"

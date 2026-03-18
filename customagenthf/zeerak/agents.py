"""Agent construction and feature execution for Zeerak."""

from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel, ToolCallingAgent

from .config import (
    EXECUTION_STYLE_GUIDANCE,
    SEARCH_ENABLED_FEATURES,
    TOOL_CALLING_FEATURES,
    load_feature_prompt,
    model_fallback_id,
    model_id_for_feature,
)
from .policy import apply_rahnama_policy, apply_tabib_policy
from .routing import route_feature


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


def run_feature(feature: str, task: str) -> str:
    if feature == "auto":
        selected_feature, reason = route_feature(task)
        answer = run_feature(selected_feature, task)
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
    agent = build_agent(feature, prefer_tool_calling=True, model_id=primary_model)
    full_task = assemble_feature_task(prompt, task)
    used_model = primary_model

    try:
        answer = str(agent.run(full_task))
    except Exception as exc:
        error_text = str(exc).lower()
        if "bad request" in error_text or "400" in error_text:
            fallback_agent = build_agent(feature, prefer_tool_calling=False, model_id=primary_model)
            answer = str(fallback_agent.run(full_task))
        elif "403" in error_text or "forbidden" in error_text or "provider" in error_text:
            used_model = model_fallback_id()
            fallback_agent = build_agent(feature, prefer_tool_calling=False, model_id=used_model)
            answer = str(fallback_agent.run(full_task))
        else:
            raise

    return f"[model] {used_model}\n\n{answer}"

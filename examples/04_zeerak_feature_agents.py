"""Zeerak feature-focused agent launcher.

This script builds one specialized smolagents CodeAgent per Zeerak feature.
Each feature uses tailored instructions and optional web-search tooling.
"""

import argparse
import os
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel, ToolCallingAgent

FEATURE_OVERVIEW = {
    "auto": "Auto-route user input to the best Zeerak feature.",
    "chat": "Conversational AI in Pashto, Dari, and English.",
    "zamvision": "Document translation, OCR guidance, and object recognition support.",
    "codekhana": "Coding mentor for Python and web development.",
    "dehqan": "Agriculture assistant for Afghan farmers.",
    "tabib": "Health triage and symptom checker with safety boundaries.",
    "hunar": "Skills guidance and CV/resume building.",
    "education": "Curriculum-aligned tutoring for Afghan classes 6-12.",
}

# Default model picks per feature. Override any value with environment variables:
# ZEERAK_MODEL_<FEATURE>, e.g. ZEERAK_MODEL_CODEKHANA.
FEATURE_MODEL_DEFAULTS = {
    "chat": "CohereForAI/aya-expanse-32b",
    "zamvision": "Qwen/Qwen2.5-VL-72B-Instruct",
    "codekhana": "Qwen/Qwen2.5-Coder-32B-Instruct",
    "dehqan": "meta-llama/Llama-3.3-70B-Instruct",
    "tabib": "microsoft/Phi-4",
    "hunar": "meta-llama/Llama-3.1-70B-Instruct",
    "education": "Qwen/Qwen2.5-72B-Instruct",
}

GLOBAL_FALLBACK_MODEL = "Qwen/Qwen3-Next-80B-A3B-Thinking"

FEATURE_PROMPTS = {
    "chat": (
        "You are Zeerak Chat, a multilingual conversational assistant for Afghan users. "
        "You can respond in Pashto, Dari, or English based on user preference. "
        "Ask which language the user prefers if unclear. Keep answers supportive and clear."
    ),
    "zamvision": (
        "You are ZamVision, a vision support assistant. "
        "Help users with OCR extraction strategy, document translation workflow, and object recognition guidance. "
        "If image content is not available, ask for text snippets, image description, or upload context."
    ),
    "codekhana": (
        "You are CodeKhana, an AI coding mentor. "
        "Teach Python and web development in small practical steps with examples and mini-exercises. "
        "Prefer learning-by-doing and explain debugging in plain language. "
        "Keep outputs concise and avoid dumping very large boilerplate blocks."
    ),
    "dehqan": (
        "You are Dehqan AI, an agriculture assistant for Afghan farmers. "
        "Provide practical advice on crops, irrigation, soil, seasonal planning, and pest handling. "
        "Ask about province, season, and crop type before making recommendations."
    ),
    "tabib": (
        "You are Tabib, a health triage helper. "
        "Provide educational symptom guidance, risk flags, and clear next steps. "
        "Do not provide definitive diagnosis. Escalate emergencies immediately and advise contacting a clinician."
    ),
    "hunar": (
        "You are Hunar, a skills and employability coach. "
        "Help users identify strengths, choose learning paths, and build a professional CV/resume. "
        "Provide role-specific bullet points and interview prep suggestions."
    ),
    "education": (
        "You are Zeerak Education, a class 6-12 learning assistant for Afghan curriculum contexts. "
        "Teach concepts with age-appropriate explanations, worked examples, and quick checks. "
        "Adjust depth based on grade level and subject."
    ),
}

EXECUTION_STYLE_GUIDANCE = (
    "When writing action code: avoid escaped triple quotes like \\\"\\\"\\\". "
    "Prefer building answers with normal strings, short paragraphs, or lists. "
    "Return practical, concise output instead of very long literal blocks."
)

ROUTER_KEYWORDS: Dict[str, List[str]] = {
    "zamvision": [
        "image",
        "photo",
        "camera",
        "ocr",
        "translate document",
        "scan",
        "object recognition",
    ],
    "codekhana": [
        "python",
        "javascript",
        "coding",
        "programming",
        "bug",
        "debug",
        "html",
        "css",
        "web development",
    ],
    "dehqan": [
        "farm",
        "farming",
        "crop",
        "wheat",
        "soil",
        "irrigation",
        "pest",
        "harvest",
        "fertilizer",
        "livestock",
    ],
    "tabib": [
        "symptom",
        "pain",
        "fever",
        "sick",
        "health",
        "hospital",
        "medicine",
        "doctor",
        "triage",
    ],
    "hunar": [
        "cv",
        "resume",
        "job",
        "career",
        "interview",
        "skills",
        "upskill",
        "cover letter",
    ],
    "education": [
        "class",
        "grade",
        "homework",
        "lesson",
        "exam",
        "math",
        "physics",
        "chemistry",
        "biology",
        "curriculum",
    ],
    "chat": [
        "pashto",
        "dari",
        "english",
        "translate",
        "conversation",
    ],
}

TABIB_EMERGENCY_KEYWORDS = [
    "chest pain",
    "cannot breathe",
    "can't breathe",
    "severe bleeding",
    "unconscious",
    "stroke",
    "heart attack",
    "suicide",
    "self-harm",
    "overdose",
    "seizure",
]

TABIB_EMERGENCY_TEMPLATE = (
    "This may be an emergency. Call local emergency services now or go to the nearest hospital immediately. "
    "If breathing is difficult, chest pain is severe, bleeding is heavy, or there is risk of self-harm, "
    "do not wait for online advice. If possible, ask a trusted person to stay with you while you seek urgent care."
)


def route_feature(task: str) -> Tuple[str, str]:
    lowered = task.lower()
    scores = {}

    for feature, keywords in ROUTER_KEYWORDS.items():
        scores[feature] = sum(1 for keyword in keywords if keyword in lowered)

    best_feature = max(scores, key=scores.get)
    best_score = scores[best_feature]

    if best_score == 0:
        return "chat", "No clear domain keywords found; defaulted to chat."

    return best_feature, f"Matched {best_score} keyword(s) for {best_feature}."


def apply_tabib_policy(task: str) -> Tuple[bool, str]:
    lowered = task.lower()

    if any(keyword in lowered for keyword in TABIB_EMERGENCY_KEYWORDS):
        return True, TABIB_EMERGENCY_TEMPLATE

    safe_prompt = (
        "Use this structured triage style: 1) possible risk level, 2) immediate self-care, "
        "3) warning signs that require urgent care, 4) when to contact a clinician. "
        "Do not give a definitive diagnosis or medication dosage."
    )
    return False, safe_prompt


def model_id_for_feature(feature: str) -> str:
    env_key = f"ZEERAK_MODEL_{feature.upper()}"
    override = os.getenv(env_key)
    if override:
        return override
    return FEATURE_MODEL_DEFAULTS.get(feature, "Qwen/Qwen3-Next-80B-A3B-Thinking")


def model_fallback_id() -> str:
    return os.getenv("ZEERAK_MODEL_FALLBACK", GLOBAL_FALLBACK_MODEL)


def build_agent(feature: str, prefer_tool_calling: bool = True, model_id: str | None = None):
    selected_model_id = model_id or model_id_for_feature(feature)
    model = InferenceClientModel(model_id=selected_model_id)

    if feature in {"dehqan", "tabib", "education", "zamvision"}:
        tools = [DuckDuckGoSearchTool()]
    else:
        tools = []

    # Use ToolCallingAgent for content-heavy features when provider supports it.
    if prefer_tool_calling and feature in {"chat", "hunar", "education"}:
        return ToolCallingAgent(tools=tools, model=model)

    return CodeAgent(tools=tools, model=model)


def run_feature(feature: str, task: str) -> str:
    if feature == "auto":
        selected_feature, reason = route_feature(task)
        answer = run_feature(selected_feature, task)
        return (
            f"[router] Selected feature: {selected_feature}. {reason}\n\n"
            f"{answer}"
        )

    prompt = FEATURE_PROMPTS[feature]

    if feature == "tabib":
        emergency, tabib_payload = apply_tabib_policy(task)
        if emergency:
            return tabib_payload
        prompt = f"{prompt} {tabib_payload}"

    primary_model = model_id_for_feature(feature)
    agent = build_agent(feature, prefer_tool_calling=True, model_id=primary_model)
    full_task = (
        f"{prompt}\n\n"
        f"Execution style: {EXECUTION_STYLE_GUIDANCE}\n\n"
        f"User request: {task}"
    )
    used_model = primary_model

    try:
        answer = str(agent.run(full_task))
    except Exception as exc:
        error_text = str(exc).lower()
        # Some providers reject tool-calling payloads; retry with CodeAgent.
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Zeerak feature-focused smolagent.")
    parser.add_argument(
        "--feature",
        required=True,
        choices=sorted(FEATURE_OVERVIEW.keys()),
        help="Zeerak feature mode to run (use 'auto' for routing).",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="User task/question for the selected feature.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    print(f"[feature] {args.feature}: {FEATURE_OVERVIEW[args.feature]}")

    if args.feature != "auto":
        print(f"[model] {model_id_for_feature(args.feature)}")

    answer = run_feature(args.feature, args.task)
    print("\n[answer]")
    print(answer)


if __name__ == "__main__":
    main()

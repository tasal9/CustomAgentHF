"""Zeerak feature-focused agent launcher.

This script builds one specialized smolagents CodeAgent per Zeerak feature.
Each feature uses tailored instructions and optional web-search tooling.
"""

import argparse

from dotenv import load_dotenv
from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel

FEATURE_OVERVIEW = {
    "chat": "Conversational AI in Pashto, Dari, and English.",
    "zamvision": "Document translation, OCR guidance, and object recognition support.",
    "codekhana": "Coding mentor for Python and web development.",
    "dehqan": "Agriculture assistant for Afghan farmers.",
    "tabib": "Health triage and symptom checker with safety boundaries.",
    "hunar": "Skills guidance and CV/resume building.",
    "education": "Curriculum-aligned tutoring for Afghan classes 6-12.",
}

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
        "Prefer learning-by-doing and explain debugging in plain language."
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


def build_agent(feature: str) -> CodeAgent:
    model = InferenceClientModel()

    if feature in {"dehqan", "tabib", "education", "zamvision"}:
        tools = [DuckDuckGoSearchTool()]
    else:
        tools = []

    return CodeAgent(tools=tools, model=model)


def run_feature(feature: str, task: str) -> str:
    prompt = FEATURE_PROMPTS[feature]
    agent = build_agent(feature)
    full_task = f"{prompt}\n\nUser request: {task}"
    return str(agent.run(full_task))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Zeerak feature-focused smolagent.")
    parser.add_argument(
        "--feature",
        required=True,
        choices=sorted(FEATURE_OVERVIEW.keys()),
        help="Zeerak feature mode to run.",
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
    answer = run_feature(args.feature, args.task)
    print("\n[answer]")
    print(answer)


if __name__ == "__main__":
    main()

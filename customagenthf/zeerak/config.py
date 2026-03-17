"""Static configuration and model selection for Zeerak feature agents."""

import os

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

SEARCH_ENABLED_FEATURES = {"dehqan", "tabib", "education", "zamvision"}
TOOL_CALLING_FEATURES = {"chat", "hunar", "education"}


def model_id_for_feature(feature: str) -> str:
    env_key = f"ZEERAK_MODEL_{feature.upper()}"
    override = os.getenv(env_key)
    if override:
        return override
    return FEATURE_MODEL_DEFAULTS.get(feature, GLOBAL_FALLBACK_MODEL)


def model_fallback_id() -> str:
    return os.getenv("ZEERAK_MODEL_FALLBACK", GLOBAL_FALLBACK_MODEL)

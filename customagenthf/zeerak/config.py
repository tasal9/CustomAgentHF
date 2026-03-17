"""Static configuration and model selection for Zeerak feature agents."""

import os
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    overview: str
    default_model_id: str | None = None
    prompt_file: str | None = None
    search_enabled: bool = False
    tool_calling_enabled: bool = False


FEATURE_SPECS = {
    "auto": FeatureSpec(
        name="auto",
        overview="Auto-route user input to the best Zeerak feature.",
    ),
    "chat": FeatureSpec(
        name="chat",
        overview="Conversational AI in Pashto, Dari, and English.",
        default_model_id="CohereForAI/aya-expanse-32b",
        prompt_file="chat.txt",
        tool_calling_enabled=True,
    ),
    "zamvision": FeatureSpec(
        name="zamvision",
        overview="Document translation, OCR guidance, and object recognition support.",
        default_model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        prompt_file="zamvision.txt",
        search_enabled=True,
    ),
    "codekhana": FeatureSpec(
        name="codekhana",
        overview="Coding mentor for Python and web development.",
        default_model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        prompt_file="codekhana.txt",
    ),
    "dehqan": FeatureSpec(
        name="dehqan",
        overview="Agriculture assistant for Afghan farmers.",
        default_model_id="meta-llama/Llama-3.3-70B-Instruct",
        prompt_file="dehqan.txt",
        search_enabled=True,
    ),
    "tabib": FeatureSpec(
        name="tabib",
        overview="Health triage and symptom checker with safety boundaries.",
        default_model_id="microsoft/Phi-4",
        prompt_file="tabib.txt",
        search_enabled=True,
    ),
    "hunar": FeatureSpec(
        name="hunar",
        overview="Skills guidance and CV/resume building.",
        default_model_id="meta-llama/Llama-3.1-70B-Instruct",
        prompt_file="hunar.txt",
        tool_calling_enabled=True,
    ),
    "education": FeatureSpec(
        name="education",
        overview="Curriculum-aligned tutoring for Afghan classes 6-12.",
        default_model_id="Qwen/Qwen2.5-72B-Instruct",
        prompt_file="education.txt",
        search_enabled=True,
        tool_calling_enabled=True,
    ),
}

FEATURE_OVERVIEW = {name: spec.overview for name, spec in FEATURE_SPECS.items()}

GLOBAL_FALLBACK_MODEL = "Qwen/Qwen3-Next-80B-A3B-Thinking"

EXECUTION_STYLE_GUIDANCE = (
    "When writing action code: avoid escaped triple quotes like \\\"\\\"\\\". "
    "Prefer building answers with normal strings, short paragraphs, or lists. "
    "Return practical, concise output instead of very long literal blocks."
)

SEARCH_ENABLED_FEATURES = {
    name for name, spec in FEATURE_SPECS.items() if spec.search_enabled
}
TOOL_CALLING_FEATURES = {
    name for name, spec in FEATURE_SPECS.items() if spec.tool_calling_enabled
}


def get_feature_spec(feature: str) -> FeatureSpec:
    return FEATURE_SPECS[feature]


@lru_cache(maxsize=None)
def load_feature_prompt(feature: str) -> str:
    feature_spec = get_feature_spec(feature)
    if not feature_spec.prompt_file:
        raise ValueError(f"Feature '{feature}' does not define a prompt file.")

    prompt_path = resources.files("customagenthf.zeerak").joinpath("prompts", feature_spec.prompt_file)
    return prompt_path.read_text(encoding="utf-8").strip()


def model_id_for_feature(feature: str) -> str:
    feature_spec = get_feature_spec(feature)
    env_key = f"ZEERAK_MODEL_{feature.upper()}"
    override = os.getenv(env_key)
    if override:
        return override
    if feature_spec.default_model_id:
        return feature_spec.default_model_id
    return GLOBAL_FALLBACK_MODEL


def model_fallback_id() -> str:
    return os.getenv("ZEERAK_MODEL_FALLBACK", GLOBAL_FALLBACK_MODEL)

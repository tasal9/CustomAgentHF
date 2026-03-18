"""Public Zeerak API."""

from .agents import FeatureRunResult, assemble_feature_task, build_agent, run_feature, run_feature_result
from .cli import main, parse_args
from .config import FEATURE_OVERVIEW, FeatureSpec, get_feature_spec, load_feature_prompt, model_fallback_id, model_id_for_feature
from .features import list_features, search_features
from .formatting import (
    OUTPUT_MODE_AUTO,
    OUTPUT_MODE_MARKDOWN,
    OUTPUT_MODE_PLAIN,
    format_education_answer,
    format_feature_answer,
    format_hunar_answer,
    format_rahnama_answer,
    format_tabib_answer,
    render_rahnama_plain_text,
)
from .rendering import feature_capabilities, format_feature_summary, render_feature_json, render_feature_output, render_feature_table
from .policy import apply_rahnama_policy, apply_tabib_policy
from .routing import route_feature
from .schemas import (
    EducationResponse,
    HunarResponse,
    RahnamaResponse,
    TabibResponse,
    parse_education_response,
    parse_hunar_response,
    parse_rahnama_response,
    parse_tabib_response,
)

__all__ = [
    "FEATURE_OVERVIEW",
    "FeatureSpec",
    "OUTPUT_MODE_AUTO",
    "OUTPUT_MODE_MARKDOWN",
    "OUTPUT_MODE_PLAIN",
    "EducationResponse",
    "FeatureRunResult",
    "HunarResponse",
    "RahnamaResponse",
    "TabibResponse",
    "apply_rahnama_policy",
    "apply_tabib_policy",
    "assemble_feature_task",
    "build_agent",
    "feature_capabilities",
    "format_education_answer",
    "format_feature_answer",
    "format_feature_summary",
    "format_hunar_answer",
    "format_rahnama_answer",
    "format_tabib_answer",
    "render_rahnama_plain_text",
    "get_feature_spec",
    "list_features",
    "load_feature_prompt",
    "main",
    "model_fallback_id",
    "model_id_for_feature",
    "parse_args",
    "parse_education_response",
    "parse_hunar_response",
    "parse_rahnama_response",
    "parse_tabib_response",
    "route_feature",
    "render_feature_json",
    "render_feature_output",
    "render_feature_table",
    "run_feature",
    "run_feature_result",
    "search_features",
]

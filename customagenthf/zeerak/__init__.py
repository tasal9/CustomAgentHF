"""Public Zeerak API."""

from .agents import assemble_feature_task, build_agent, run_feature
from .cli import main, parse_args
from .config import FEATURE_OVERVIEW, FeatureSpec, get_feature_spec, load_feature_prompt, model_fallback_id, model_id_for_feature
from .features import list_features, search_features
from .formatting import format_feature_answer, format_rahnama_answer
from .rendering import feature_capabilities, format_feature_summary, render_feature_json, render_feature_output, render_feature_table
from .policy import apply_rahnama_policy, apply_tabib_policy
from .routing import route_feature

__all__ = [
    "FEATURE_OVERVIEW",
    "FeatureSpec",
    "apply_rahnama_policy",
    "apply_tabib_policy",
    "assemble_feature_task",
    "build_agent",
    "feature_capabilities",
    "format_feature_answer",
    "format_feature_summary",
    "format_rahnama_answer",
    "get_feature_spec",
    "list_features",
    "load_feature_prompt",
    "main",
    "model_fallback_id",
    "model_id_for_feature",
    "parse_args",
    "route_feature",
    "render_feature_json",
    "render_feature_output",
    "render_feature_table",
    "run_feature",
    "search_features",
]

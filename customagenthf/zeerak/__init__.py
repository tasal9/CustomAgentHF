"""Public Zeerak API."""

from .agents import assemble_feature_task, build_agent, run_feature
from .cli import main, parse_args
from .config import FEATURE_OVERVIEW, FeatureSpec, get_feature_spec, load_feature_prompt, model_fallback_id, model_id_for_feature
from .features import feature_capabilities, format_feature_summary, list_features, render_feature_table, search_features
from .policy import apply_tabib_policy
from .routing import route_feature

__all__ = [
    "FEATURE_OVERVIEW",
    "FeatureSpec",
    "apply_tabib_policy",
    "assemble_feature_task",
    "build_agent",
    "feature_capabilities",
    "format_feature_summary",
    "get_feature_spec",
    "list_features",
    "load_feature_prompt",
    "main",
    "model_fallback_id",
    "model_id_for_feature",
    "parse_args",
    "route_feature",
    "render_feature_table",
    "run_feature",
    "search_features",
]

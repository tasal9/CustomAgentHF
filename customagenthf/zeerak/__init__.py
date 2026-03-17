"""Public Zeerak API."""

from .agents import build_agent, run_feature
from .cli import main, parse_args
from .config import FEATURE_OVERVIEW, model_fallback_id, model_id_for_feature
from .policy import apply_tabib_policy
from .routing import route_feature

__all__ = [
    "FEATURE_OVERVIEW",
    "apply_tabib_policy",
    "build_agent",
    "main",
    "model_fallback_id",
    "model_id_for_feature",
    "parse_args",
    "route_feature",
    "run_feature",
]

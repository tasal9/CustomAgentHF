"""Reusable smolagents helpers and Zeerak feature agents."""

from .backends import run_with_hf_inference, run_with_litellm, run_with_transformers
from .basic import build_minimal_agent, run_minimal_task
from .search import build_search_agent, run_search_task
from .zeerak import FEATURE_OVERVIEW, run_feature

__all__ = [
    "FEATURE_OVERVIEW",
    "build_minimal_agent",
    "build_search_agent",
    "run_feature",
    "run_minimal_task",
    "run_search_task",
    "run_with_hf_inference",
    "run_with_litellm",
    "run_with_transformers",
]

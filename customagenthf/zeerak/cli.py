"""CLI entry points for Zeerak feature agents."""

import argparse

from dotenv import load_dotenv

from .agents import run_feature
from .config import FEATURE_OVERVIEW, model_id_for_feature


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)

    print(f"[feature] {args.feature}: {FEATURE_OVERVIEW[args.feature]}")

    if args.feature != "auto":
        print(f"[model] {model_id_for_feature(args.feature)}")

    answer = run_feature(args.feature, args.task)
    print("\n[answer]")
    print(answer)

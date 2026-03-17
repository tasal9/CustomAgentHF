"""CLI entry points for Zeerak feature agents."""

import argparse

from dotenv import load_dotenv

from .agents import run_feature
from .config import FEATURE_OVERVIEW, model_id_for_feature
from .features import list_features, render_feature_table, search_features


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Zeerak feature-focused smolagent.")
    parser.add_argument(
        "--list-features",
        action="store_true",
        help="List available Zeerak features and exit.",
    )
    parser.add_argument(
        "--search-features",
        help="Filter features by name or overview and exit.",
    )
    parser.add_argument(
        "--feature",
        choices=sorted(FEATURE_OVERVIEW.keys()),
        help="Zeerak feature mode to run (use 'auto' for routing).",
    )
    parser.add_argument(
        "--task",
        help="User task/question for the selected feature.",
    )
    args = parser.parse_args(argv)

    if args.list_features and args.search_features:
        parser.error("--list-features and --search-features cannot be used together")

    if not args.list_features and not args.search_features and (not args.feature or not args.task):
        parser.error("the following arguments are required: --feature, --task")

    return args


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)

    if args.list_features:
        print(render_feature_table(list_features()))
        return

    if args.search_features:
        print(render_feature_table(search_features(args.search_features)))
        return

    print(f"[feature] {args.feature}: {FEATURE_OVERVIEW[args.feature]}")

    if args.feature != "auto":
        print(f"[model] {model_id_for_feature(args.feature)}")

    answer = run_feature(args.feature, args.task)
    print("\n[answer]")
    print(answer)

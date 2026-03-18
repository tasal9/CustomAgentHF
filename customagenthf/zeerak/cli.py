"""CLI entry points for Zeerak feature agents."""

import argparse
import shutil

from dotenv import load_dotenv

from .agents import run_feature
from .config import FEATURE_OVERVIEW, model_id_for_feature
from .features import list_features, search_features
from .rendering import render_feature_output


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
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format for feature discovery commands.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        help="Maximum table width for feature discovery output.",
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Disable truncation and print full-width discovery tables.",
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

    if args.output != "table" and not args.list_features and not args.search_features:
        parser.error("--output can only be used with --list-features or --search-features")

    if args.max_width is not None and args.max_width <= 0:
        parser.error("--max-width must be a positive integer")

    if args.max_width is not None and args.output != "table":
        parser.error("--max-width can only be used with --output table")

    if args.no_truncate and args.output != "table":
        parser.error("--no-truncate can only be used with --output table")

    if not args.list_features and not args.search_features and (not args.feature or not args.task):
        parser.error("the following arguments are required: --feature, --task")

    return args


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)
    terminal_width = args.max_width
    if terminal_width is None and args.output == "table":
        terminal_width = shutil.get_terminal_size(fallback=(120, 24)).columns

    if args.list_features:
        print(
            render_feature_output(
                list_features(),
                output_format=args.output,
                max_width=terminal_width,
                truncate=not args.no_truncate,
            )
        )
        return

    if args.search_features:
        print(
            render_feature_output(
                search_features(args.search_features),
                output_format=args.output,
                max_width=terminal_width,
                truncate=not args.no_truncate,
            )
        )
        return

    print(f"[feature] {args.feature}: {FEATURE_OVERVIEW[args.feature]}")

    answer = run_feature(args.feature, args.task)
    print("\n[answer]")
    print(answer)

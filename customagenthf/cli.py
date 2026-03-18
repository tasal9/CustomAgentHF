import argparse

from .backends import DEFAULT_TASK as BACKENDS_DEFAULT_TASK
from .backends import run_with_hf_inference, run_with_litellm, run_with_transformers
from .basic import DEFAULT_TASK as MINIMAL_DEFAULT_TASK
from .basic import run_minimal_task
from .search import DEFAULT_TASK as SEARCH_DEFAULT_TASK
from .search import run_search_task
from .zeerak import FEATURE_OVERVIEW, main as zeerak_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run reusable smolagents demos and Zeerak agents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    minimal_parser = subparsers.add_parser("minimal", help="Run the minimal code agent demo.")
    minimal_parser.add_argument("--task", default=MINIMAL_DEFAULT_TASK, help="Task to send to the agent.")

    search_parser = subparsers.add_parser("search", help="Run the search-enabled code agent demo.")
    search_parser.add_argument("--task", default=SEARCH_DEFAULT_TASK, help="Task to send to the agent.")

    backends_parser = subparsers.add_parser("backends", help="Run a backend example.")
    backends_parser.add_argument(
        "--backend",
        choices=["hf", "litellm", "transformers"],
        default="hf",
        help="Model backend to use.",
    )
    backends_parser.add_argument("--task", default=BACKENDS_DEFAULT_TASK, help="Task to send to the agent.")
    backends_parser.add_argument("--model-id", default=None, help="Optional model override for the selected backend.")

    zeerak_parser = subparsers.add_parser("zeerak", help="Run a Zeerak feature agent.")
    zeerak_parser.add_argument(
        "--list-features",
        action="store_true",
        help="List available Zeerak features and exit.",
    )
    zeerak_parser.add_argument(
        "--search-features",
        help="Filter features by name or overview and exit.",
    )
    zeerak_parser.add_argument(
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format for feature discovery commands.",
    )
    zeerak_parser.add_argument(
        "--max-width",
        type=int,
        help="Maximum table width for feature discovery output.",
    )
    zeerak_parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Disable truncation and print full-width discovery tables.",
    )
    zeerak_parser.add_argument(
        "--feature",
        choices=sorted(FEATURE_OVERVIEW.keys()),
        help="Zeerak feature mode to run.",
    )
    zeerak_parser.add_argument("--task", help="User task or question.")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "minimal":
        print(run_minimal_task(task=args.task))
        return

    if args.command == "search":
        print(run_search_task(task=args.task))
        return

    if args.command == "backends":
        backend_runners = {
            "hf": run_with_hf_inference,
            "litellm": run_with_litellm,
            "transformers": run_with_transformers,
        }
        runner = backend_runners[args.backend]
        runner_kwargs = {"task": args.task}
        if args.model_id:
            runner_kwargs["model_id"] = args.model_id
        print(runner(**runner_kwargs))
        return

    if args.command == "zeerak":
        zeerak_args = []
        if args.list_features:
            zeerak_args.append("--list-features")
        if args.search_features:
            zeerak_args.extend(["--search-features", args.search_features])
        if args.output:
            zeerak_args.extend(["--output", args.output])
        if args.max_width is not None:
            zeerak_args.extend(["--max-width", str(args.max_width)])
        if args.no_truncate:
            zeerak_args.append("--no-truncate")
        if args.feature:
            zeerak_args.extend(["--feature", args.feature])
        if args.task:
            zeerak_args.extend(["--task", args.task])
        zeerak_main(zeerak_args)
        return

    parser.error(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()

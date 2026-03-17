"""Rendering helpers for Zeerak feature discovery output."""

import json
import shutil

from .config import FeatureSpec

DISCOVERY_HEADERS = ["feature", "capabilities", "default-model", "overview"]
DISCOVERY_MIN_WIDTHS = [7, 12, 13, 20]
DISCOVERY_REDUCTION_ORDER = [3, 2, 1]


def feature_capabilities(feature: FeatureSpec) -> str:
    capabilities = []
    if feature.search_enabled:
        capabilities.append("search")
    if feature.tool_calling_enabled:
        capabilities.append("tool-calling")
    if not capabilities:
        return "-"
    return ", ".join(capabilities)


def feature_to_dict(feature: FeatureSpec) -> dict[str, object]:
    capabilities = feature_capabilities(feature)
    return {
        "name": feature.name,
        "overview": feature.overview,
        "default_model_id": feature.default_model_id,
        "search_enabled": feature.search_enabled,
        "tool_calling_enabled": feature.tool_calling_enabled,
        "capabilities": capabilities.split(", ") if capabilities != "-" else [],
    }


def format_feature_summary(feature: FeatureSpec) -> str:
    if feature.default_model_id:
        return f"{feature.name}: {feature.overview} [default-model: {feature.default_model_id}]"
    return f"{feature.name}: {feature.overview}"


def render_feature_json(features: list[FeatureSpec]) -> str:
    return json.dumps([feature_to_dict(feature) for feature in features], indent=2)


def _truncate_cell(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 3:
        return "." * width
    return f"{text[: width - 3]}..."


def _fit_widths(rows: list[list[str]], max_width: int | None) -> list[int]:
    widths = [len(header) for header in DISCOVERY_HEADERS]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    if max_width is None:
        max_width = shutil.get_terminal_size(fallback=(120, 24)).columns

    total_width = sum(widths) + 3 * (len(widths) - 1)
    if total_width <= max_width:
        return widths

    overshoot = total_width - max_width
    for index in DISCOVERY_REDUCTION_ORDER:
        minimum = max(DISCOVERY_MIN_WIDTHS[index], len(DISCOVERY_HEADERS[index]))
        available_reduction = widths[index] - minimum
        if available_reduction <= 0:
            continue

        reduction = min(available_reduction, overshoot)
        widths[index] -= reduction
        overshoot -= reduction
        if overshoot == 0:
            break

    return widths


def render_feature_table(features: list[FeatureSpec], max_width: int | None = None) -> str:
    rows = [
        [
            feature.name,
            feature_capabilities(feature),
            feature.default_model_id or "-",
            feature.overview,
        ]
        for feature in features
    ]

    widths = _fit_widths(rows, max_width=max_width)

    def format_row(row: list[str]) -> str:
        cells = []
        for index, cell in enumerate(row):
            cells.append(_truncate_cell(cell, widths[index]).ljust(widths[index]))
        return " | ".join(cells)

    separator = "-+-".join("-" * width for width in widths)
    table_rows = [format_row(DISCOVERY_HEADERS), separator]
    table_rows.extend(format_row(row) for row in rows)
    return "\n".join(table_rows)


def render_feature_output(features: list[FeatureSpec], output_format: str, max_width: int | None = None) -> str:
    if output_format == "json":
        return render_feature_json(features)
    return render_feature_table(features, max_width=max_width)
"""Helpers for discovering Zeerak feature metadata."""

from .config import FEATURE_SPECS, FeatureSpec


def list_features(include_auto: bool = True) -> list[FeatureSpec]:
    features = list(FEATURE_SPECS.values())
    if include_auto:
        return features
    return [feature for feature in features if feature.name != "auto"]


def search_features(query: str, include_auto: bool = True) -> list[FeatureSpec]:
    lowered_query = query.strip().lower()
    if not lowered_query:
        return list_features(include_auto=include_auto)

    return [
        feature
        for feature in list_features(include_auto=include_auto)
        if lowered_query in feature.name.lower() or lowered_query in feature.overview.lower()
    ]


def format_feature_summary(feature: FeatureSpec) -> str:
    if feature.default_model_id:
        return f"{feature.name}: {feature.overview} [default-model: {feature.default_model_id}]"
    return f"{feature.name}: {feature.overview}"


def feature_capabilities(feature: FeatureSpec) -> str:
    capabilities = []
    if feature.search_enabled:
        capabilities.append("search")
    if feature.tool_calling_enabled:
        capabilities.append("tool-calling")
    if not capabilities:
        return "-"
    return ", ".join(capabilities)


def render_feature_table(features: list[FeatureSpec]) -> str:
    headers = ["feature", "capabilities", "default-model", "overview"]
    rows = [
        [
            feature.name,
            feature_capabilities(feature),
            feature.default_model_id or "-",
            feature.overview,
        ]
        for feature in features
    ]

    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def format_row(row: list[str]) -> str:
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))

    separator = "-+-".join("-" * width for width in widths)
    table_rows = [format_row(headers), separator]
    table_rows.extend(format_row(row) for row in rows)
    return "\n".join(table_rows)

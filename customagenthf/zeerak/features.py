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
        if lowered_query in feature.name.lower()
        or lowered_query in feature.overview.lower()
        or any(lowered_query in alias.lower() for alias in feature.routing_aliases)
        or any(lowered_query in tag.lower() for tag in feature.routing_tags)
    ]

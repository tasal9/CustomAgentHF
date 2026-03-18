"""Signal-based routing for Zeerak feature selection."""

from typing import Tuple

from .config import FEATURE_SPECS

ROUTING_ALIAS_WEIGHT = 3
ROUTING_TAG_WEIGHT = 1


def route_feature(task: str) -> Tuple[str, str]:
    lowered = task.lower()
    scores = {}
    reasons = {}

    for feature, spec in FEATURE_SPECS.items():
        if feature == "auto":
            continue

        alias_hits = [alias for alias in spec.routing_aliases if alias in lowered]
        tag_hits = [tag for tag in spec.routing_tags if tag in lowered]
        score = len(alias_hits) * ROUTING_ALIAS_WEIGHT + len(tag_hits) * ROUTING_TAG_WEIGHT
        scores[feature] = score
        reasons[feature] = (alias_hits, tag_hits)

    best_feature = max(scores, key=scores.get)
    best_score = scores[best_feature]

    if best_score == 0:
        return "chat", "No clear domain keywords found; defaulted to chat."

    alias_hits, tag_hits = reasons[best_feature]
    return (
        best_feature,
        f"Matched score {best_score} for {best_feature} from {len(alias_hits)} alias hit(s) and {len(tag_hits)} tag hit(s).",
    )

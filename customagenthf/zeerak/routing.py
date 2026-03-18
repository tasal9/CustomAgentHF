"""Signal-based routing for Zeerak feature selection."""

from typing import Tuple

from .config import FEATURE_SPECS, ROUTING_CONFIDENCE_THRESHOLD

ROUTING_ALIAS_WEIGHT = 3
ROUTING_TAG_WEIGHT = 1
ROUTING_NEGATIVE_WEIGHT = 2


def route_feature(task: str) -> Tuple[str, str]:
    lowered = task.lower()
    scores = {}
    reasons = {}

    for feature, spec in FEATURE_SPECS.items():
        if feature == "auto":
            continue

        alias_weight = spec.routing_alias_weight if spec.routing_alias_weight is not None else ROUTING_ALIAS_WEIGHT
        tag_weight = spec.routing_tag_weight if spec.routing_tag_weight is not None else ROUTING_TAG_WEIGHT

        alias_hits = [alias for alias in spec.routing_aliases if alias in lowered]
        tag_hits = [tag for tag in spec.routing_tags if tag in lowered]
        negative_hits = [sig for sig in spec.routing_negative_signals if sig in lowered]

        score = (
            len(alias_hits) * alias_weight
            + len(tag_hits) * tag_weight
            - len(negative_hits) * ROUTING_NEGATIVE_WEIGHT
        )
        scores[feature] = score
        reasons[feature] = (alias_hits, tag_hits, negative_hits)

    best_feature = max(scores, key=scores.get)
    best_score = scores[best_feature]

    if best_score < ROUTING_CONFIDENCE_THRESHOLD:
        reason = (
            "No clear domain keywords found; defaulted to chat."
            if best_score == 0
            else f"Confidence score {best_score} is below threshold {ROUTING_CONFIDENCE_THRESHOLD}; defaulted to chat."
        )
        return "chat", reason

    alias_hits, tag_hits, negative_hits = reasons[best_feature]
    return (
        best_feature,
        f"Matched score {best_score} for {best_feature} from {len(alias_hits)} alias hit(s) and {len(tag_hits)} tag hit(s).",
    )

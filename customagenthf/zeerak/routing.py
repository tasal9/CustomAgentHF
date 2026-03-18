"""Keyword-based routing for Zeerak feature selection."""

from typing import Dict, List, Tuple

ROUTER_KEYWORDS: Dict[str, List[str]] = {
    "zamvision": [
        "image",
        "photo",
        "camera",
        "ocr",
        "translate document",
        "scan",
        "object recognition",
    ],
    "codekhana": [
        "python",
        "javascript",
        "coding",
        "programming",
        "bug",
        "debug",
        "html",
        "css",
        "web development",
    ],
    "dehqan": [
        "farm",
        "farming",
        "crop",
        "wheat",
        "soil",
        "irrigation",
        "pest",
        "harvest",
        "fertilizer",
        "livestock",
    ],
    "tabib": [
        "symptom",
        "pain",
        "fever",
        "sick",
        "health",
        "hospital",
        "medicine",
        "doctor",
        "triage",
    ],
    "hunar": [
        "cv",
        "resume",
        "job",
        "career",
        "interview",
        "skills",
        "upskill",
        "cover letter",
    ],
    "rahnama": [
        "passport",
        "tazkira",
        "document",
        "application",
        "office",
        "service",
        "registration",
        "bill",
        "bank",
        "permit",
    ],
    "education": [
        "class",
        "grade",
        "homework",
        "lesson",
        "exam",
        "math",
        "physics",
        "chemistry",
        "biology",
        "curriculum",
    ],
    "chat": [
        "pashto",
        "dari",
        "english",
        "translate",
        "conversation",
    ],
}


def route_feature(task: str) -> Tuple[str, str]:
    lowered = task.lower()
    scores = {}

    for feature, keywords in ROUTER_KEYWORDS.items():
        scores[feature] = sum(1 for keyword in keywords if keyword in lowered)

    best_feature = max(scores, key=scores.get)
    best_score = scores[best_feature]

    if best_score == 0:
        return "chat", "No clear domain keywords found; defaulted to chat."

    return best_feature, f"Matched {best_score} keyword(s) for {best_feature}."

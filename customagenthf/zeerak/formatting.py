"""Answer formatting helpers for Zeerak features."""

import re


RAHNAMA_SECTION_PATTERNS = (
    (r"(?im)^\s*1[\.)]\s*(?:\*\*)?Likely purpose of the process(?:\*\*)?\s*:?\s*", "## Likely Purpose\n"),
    (
        r"(?im)^\s*2[\.)]\s*(?:\*\*)?Common documents or information typically needed(?:\*\*)?\s*:?\s*",
        "## Common Documents And Information\n",
    ),
    (r"(?im)^\s*3[\.)]\s*(?:\*\*)?Suggested next steps(?:\*\*)?\s*:?\s*", "## Suggested Next Steps\n"),
    (
        r"(?im)^\s*4[\.)]\s*(?:\*\*)?Where local office rules may differ(?:\*\*)?\s*:?\s*",
        "## Local Office Differences\n",
    ),
    (r"(?im)^\s*[!\u26A0\uFE0F ]*(?:\*\*)?Important(?:\*\*)?\s*:?\s*", "## Verification Note\n"),
    (r"(?im)^\s*>?\s*(?:\*\*)?Note(?:\*\*)?\s*:?\s*", "## Verification Note\n"),
)


def format_rahnama_answer(answer: str) -> str:
    """Normalize Rahnama answers into cleaner markdown sections."""

    formatted = answer.replace("\r\n", "\n").strip()
    formatted = re.sub(r"(?is)^final answer:\s*", "", formatted)

    for pattern, replacement in RAHNAMA_SECTION_PATTERNS:
        formatted = re.sub(pattern, replacement, formatted)

    formatted = re.sub(r"(?m)^\s*[-*]\s+", "- ", formatted)
    formatted = re.sub(r"(?m)^\s{2,}[-*]\s+", "- ", formatted)
    formatted = re.sub(r"(?m)[ \t]+$", "", formatted)
    formatted = re.sub(r"(?m)^(## .+)$", r"\n\1", formatted)
    formatted = re.sub(r"\n{3,}", "\n\n", formatted)

    return formatted.strip()


def format_feature_answer(feature: str, answer: str) -> str:
    if feature == "rahnama":
        return format_rahnama_answer(answer)

    return answer.strip()
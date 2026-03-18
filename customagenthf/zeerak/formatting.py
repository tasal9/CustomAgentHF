"""Answer formatting helpers for Zeerak features."""

import re
from textwrap import fill


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

NARROW_TEXT_WIDTH = 72


def _wrap_text_block(text: str, width: int, initial_indent: str = "", subsequent_indent: str = "") -> str:
    return fill(
        text,
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def render_rahnama_plain_text(markdown: str, width: int) -> str:
    """Render sectioned Rahnama markdown into wrapped plain text for narrow terminals."""

    rendered_blocks: list[str] = []
    paragraph_lines: list[str] = []
    bullet_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            paragraph = " ".join(paragraph_lines)
            rendered_blocks.append(_wrap_text_block(paragraph, width=width))
            paragraph_lines.clear()

    def flush_bullets() -> None:
        if bullet_lines:
            rendered_blocks.append("\n".join(bullet_lines))
            bullet_lines.clear()

    for raw_line in markdown.strip().splitlines():
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            flush_bullets()
            continue

        if line.startswith("## "):
            flush_paragraph()
            flush_bullets()
            rendered_blocks.append(line[3:].strip().upper())
            continue

        if line.startswith("- "):
            flush_paragraph()
            bullet_text = line[2:].strip()
            bullet_lines.append(_wrap_text_block(bullet_text, width=width, initial_indent="- ", subsequent_indent="  "))
            continue

        flush_bullets()
        paragraph_lines.append(line)

    flush_paragraph()
    flush_bullets()

    return "\n\n".join(rendered_blocks)


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


def format_feature_answer(feature: str, answer: str, max_width: int | None = None) -> str:
    if feature == "rahnama":
        formatted = format_rahnama_answer(answer)
        if max_width is not None and max_width <= NARROW_TEXT_WIDTH:
            return render_rahnama_plain_text(formatted, width=max_width)
        return formatted

    return answer.strip()
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

TABIB_SECTION_PATTERNS = (
    (r"(?im)^\s*1[\.)]\s*(?:\*\*)?[Pp]ossible risk level(?:\*\*)?\s*:?\s*", "## Risk Level\n"),
    (r"(?im)^\s*2[\.)]\s*(?:\*\*)?[Ii]mmediate self[\-\s]?care(?:\*\*)?\s*:?\s*", "## Immediate Self-Care\n"),
    (
        r"(?im)^\s*3[\.)]\s*(?:\*\*)?[Ww]arning signs(?: that require urgent care)?(?:\*\*)?\s*:?\s*",
        "## Warning Signs\n",
    ),
    (
        r"(?im)^\s*4[\.)]\s*(?:\*\*)?[Ww]hen to(?: contact a| see a?)? clinician(?:\*\*)?\s*:?\s*",
        "## When To See A Clinician\n",
    ),
    (r"(?im)^\s*[!\u26A0\uFE0F ]*(?:\*\*)?Important(?:\*\*)?\s*:?\s*", "## Important\n"),
)

HUNAR_SECTION_PATTERNS = (
    (r"(?im)^\s*(?:\*\*)?[Ss]ummary(?:\*\*)?\s*:?\s*$", "## Summary\n"),
    (r"(?im)^\s*(?:\*\*)?[Kk]ey [Ss]kills?(?:\*\*)?\s*:?\s*$", "## Skills\n"),
    (r"(?im)^\s*(?:\*\*)?[Ww]ork [Ee]xperience(?:\*\*)?\s*:?\s*$", "## Experience\n"),
    (r"(?im)^\s*(?:\*\*)?[Ee]xperience(?:\*\*)?\s*:?\s*$", "## Experience\n"),
    (r"(?im)^\s*(?:\*\*)?[Rr]ecommendations?(?:\*\*)?\s*:?\s*$", "## Recommendations\n"),
    (r"(?im)^\s*(?:\*\*)?[Nn]ext [Ss]teps?(?:\*\*)?\s*:?\s*$", "## Recommendations\n"),
    (r"(?im)^\s*(?:\*\*)?[Cc]areer [Tt]ips?(?:\*\*)?\s*:?\s*$", "## Recommendations\n"),
)

EDUCATION_SECTION_PATTERNS = (
    (r"(?im)^\s*(?:\*\*)?[Ll]esson(?: [Oo]verview)?(?:\*\*)?\s*:?\s*$", "## Lesson\n"),
    (r"(?im)^\s*(?:\*\*)?[Ee]xplanation(?:\*\*)?\s*:?\s*$", "## Lesson\n"),
    (r"(?im)^\s*(?:\*\*)?[Cc]oncept(?:\*\*)?\s*:?\s*$", "## Lesson\n"),
    (r"(?im)^\s*(?:\*\*)?[Ee]xamples?(?:\*\*)?\s*:?\s*$", "## Examples\n"),
    (r"(?im)^\s*(?:\*\*)?[Ww]orked [Ee]xamples?(?:\*\*)?\s*:?\s*$", "## Examples\n"),
    (r"(?im)^\s*(?:\*\*)?[Pp]ractice [Pp]roblem(?:\*\*)?\s*:?\s*$", "## Exercises\n"),
    (r"(?im)^\s*(?:\*\*)?[Ee]xercises?(?:\*\*)?\s*:?\s*$", "## Exercises\n"),
    (r"(?im)^\s*(?:\*\*)?[Aa]nswer [Kk]ey(?:\*\*)?\s*:?\s*$", "## Answer Key\n"),
    (r"(?im)^\s*(?:\*\*)?[Ss]olution(?:\*\*)?\s*:?\s*$", "## Answer Key\n"),
    (r"(?im)^\s*(?:\*\*)?[Aa]nswers?(?:\*\*)?\s*:?\s*$", "## Answer Key\n"),
)

NARROW_TEXT_WIDTH = 72

OUTPUT_MODE_AUTO = "auto"
OUTPUT_MODE_PLAIN = "plain"
OUTPUT_MODE_MARKDOWN = "markdown"

_BULLET_PATTERN = r"[-*\u2022]"


def _wrap_text_block(text: str, width: int, initial_indent: str = "", subsequent_indent: str = "") -> str:
    return fill(
        text,
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def _render_markdown_plain_text(markdown: str, width: int) -> str:
    """Render sectioned markdown (## headings, bullet lists) into wrapped plain text."""

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


def render_rahnama_plain_text(markdown: str, width: int) -> str:
    """Render sectioned Rahnama markdown into wrapped plain text for narrow terminals."""
    return _render_markdown_plain_text(markdown, width=width)


def _normalize_sections(answer: str, section_patterns: tuple) -> str:
    """Apply section-pattern normalization and common bullet/whitespace cleanup."""
    formatted = answer.replace("\r\n", "\n").strip()
    formatted = re.sub(r"(?is)^final answer:\s*", "", formatted)

    for pattern, replacement in section_patterns:
        formatted = re.sub(pattern, replacement, formatted)

    formatted = re.sub(rf"(?m)^\s*{_BULLET_PATTERN}\s+", "- ", formatted)
    formatted = re.sub(rf"(?m)^\s{{2,}}{_BULLET_PATTERN}\s+", "- ", formatted)
    formatted = re.sub(r"(?m)[ \t]+$", "", formatted)
    formatted = re.sub(r"(?m)^(## .+)$", r"\n\1", formatted)
    formatted = re.sub(r"\n{3,}", "\n\n", formatted)

    return formatted.strip()


def format_rahnama_answer(answer: str) -> str:
    """Normalize Rahnama answers into cleaner markdown sections."""
    return _normalize_sections(answer, RAHNAMA_SECTION_PATTERNS)


def format_tabib_answer(answer: str) -> str:
    """Normalize Tabib triage answers into structured markdown sections."""
    return _normalize_sections(answer, TABIB_SECTION_PATTERNS)


def format_hunar_answer(answer: str) -> str:
    """Normalize Hunar CV/career answers into structured markdown sections."""
    return _normalize_sections(answer, HUNAR_SECTION_PATTERNS)


def format_education_answer(answer: str) -> str:
    """Normalize Education tutoring answers into structured markdown sections."""
    return _normalize_sections(answer, EDUCATION_SECTION_PATTERNS)


_FEATURE_FORMATTERS = {
    "rahnama": format_rahnama_answer,
    "tabib": format_tabib_answer,
    "hunar": format_hunar_answer,
    "education": format_education_answer,
}

_PLAIN_TEXT_FEATURES = {"rahnama", "tabib", "hunar", "education"}


def format_feature_answer(
    feature: str,
    answer: str,
    max_width: int | None = None,
    output_mode: str = OUTPUT_MODE_AUTO,
) -> str:
    """Format a feature answer for display.

    Parameters
    ----------
    feature:
        Zeerak feature name (e.g. "rahnama", "tabib").
    answer:
        Raw answer string from the agent.
    max_width:
        Terminal width hint used in auto mode to choose plain vs markdown.
    output_mode:
        ``"auto"`` (default) – use plain text when ``max_width <= NARROW_TEXT_WIDTH``,
        markdown otherwise.
        ``"plain"`` – always render as plain text (ignores terminal width).
        ``"markdown"`` – always render as markdown (ignores terminal width).
    """
    formatter = _FEATURE_FORMATTERS.get(feature)
    if formatter is None:
        return answer.strip()

    formatted = formatter(answer)

    if feature not in _PLAIN_TEXT_FEATURES:
        return formatted

    if output_mode == OUTPUT_MODE_PLAIN:
        width = max_width if max_width and max_width > 0 else NARROW_TEXT_WIDTH
        return _render_markdown_plain_text(formatted, width=width)

    if output_mode == OUTPUT_MODE_MARKDOWN:
        return formatted

    # auto mode: use plain text only when the terminal is narrow
    if max_width is not None and max_width <= NARROW_TEXT_WIDTH:
        return _render_markdown_plain_text(formatted, width=max_width)

    return formatted

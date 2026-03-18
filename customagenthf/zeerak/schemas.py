"""Typed response schemas for deterministic rendering of Zeerak feature output."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RahnamaResponse:
    """Structured representation of a Rahnama guidance answer."""

    likely_purpose: str = ""
    common_documents: str = ""
    next_steps: str = ""
    local_differences: str = ""
    verification_note: str = ""
    raw: str = ""


@dataclass(frozen=True)
class TabibResponse:
    """Structured representation of a Tabib triage answer."""

    risk_level: str = ""
    immediate_self_care: str = ""
    warning_signs: str = ""
    when_to_see_clinician: str = ""
    raw: str = ""


@dataclass(frozen=True)
class HunarResponse:
    """Structured representation of a Hunar CV/career answer."""

    summary: str = ""
    skills: str = ""
    experience: str = ""
    recommendations: str = ""
    raw: str = ""


@dataclass(frozen=True)
class EducationResponse:
    """Structured representation of an Education tutoring answer."""

    lesson: str = ""
    examples: str = ""
    exercises: str = ""
    answer_key: str = ""
    raw: str = ""


def _parse_markdown_sections(markdown: str) -> dict[str, str]:
    """Parse a ``## Section Name`` markdown string into a {name: content} dict."""
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            sections.setdefault(current_section, [])
        elif current_section is not None:
            sections[current_section].append(line)

    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def parse_rahnama_response(markdown: str) -> RahnamaResponse:
    """Parse a formatted Rahnama markdown answer into a typed RahnamaResponse."""
    s = _parse_markdown_sections(markdown)
    return RahnamaResponse(
        likely_purpose=s.get("Likely Purpose", ""),
        common_documents=s.get("Common Documents And Information", ""),
        next_steps=s.get("Suggested Next Steps", ""),
        local_differences=s.get("Local Office Differences", ""),
        verification_note=s.get("Verification Note", ""),
        raw=markdown,
    )


def parse_tabib_response(markdown: str) -> TabibResponse:
    """Parse a formatted Tabib markdown answer into a typed TabibResponse."""
    s = _parse_markdown_sections(markdown)
    return TabibResponse(
        risk_level=s.get("Risk Level", ""),
        immediate_self_care=s.get("Immediate Self-Care", ""),
        warning_signs=s.get("Warning Signs", ""),
        when_to_see_clinician=s.get("When To See A Clinician", ""),
        raw=markdown,
    )


def parse_hunar_response(markdown: str) -> HunarResponse:
    """Parse a formatted Hunar markdown answer into a typed HunarResponse."""
    s = _parse_markdown_sections(markdown)
    return HunarResponse(
        summary=s.get("Summary", ""),
        skills=s.get("Skills", ""),
        experience=s.get("Experience", ""),
        recommendations=s.get("Recommendations", ""),
        raw=markdown,
    )


def parse_education_response(markdown: str) -> EducationResponse:
    """Parse a formatted Education markdown answer into a typed EducationResponse."""
    s = _parse_markdown_sections(markdown)
    return EducationResponse(
        lesson=s.get("Lesson", ""),
        examples=s.get("Examples", ""),
        exercises=s.get("Exercises", ""),
        answer_key=s.get("Answer Key", ""),
        raw=markdown,
    )

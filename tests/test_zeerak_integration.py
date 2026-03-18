"""Integration tests for Zeerak CLI with mocked runtime paths."""

import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from customagenthf.zeerak.cli import main
from customagenthf.zeerak.agents import run_feature
from customagenthf.zeerak.formatting import (
    OUTPUT_MODE_AUTO,
    OUTPUT_MODE_MARKDOWN,
    OUTPUT_MODE_PLAIN,
    format_feature_answer,
    format_tabib_answer,
    format_hunar_answer,
    format_education_answer,
)
from customagenthf.zeerak.routing import route_feature
from customagenthf.zeerak.schemas import (
    parse_rahnama_response,
    parse_tabib_response,
    parse_hunar_response,
    parse_education_response,
)


# ---------------------------------------------------------------------------
# Forceable output modes
# ---------------------------------------------------------------------------


class ForceOutputModeTests(unittest.TestCase):
    """Tests for --plain-text and --markdown CLI flags and output_mode parameter."""

    _RAHNAMA_MARKDOWN = (
        "## Likely Purpose\n"
        "Renewing a passport helps with travel.\n\n"
        "## Suggested Next Steps\n"
        "- Visit the passport office.\n"
        "- Bring required documents."
    )

    def _run_main_with_mocked_feature(self, argv: list[str], mocked_answer: str) -> str:
        captured = StringIO()
        with patch(
            "customagenthf.zeerak.cli.run_feature",
            return_value=mocked_answer,
        ), redirect_stdout(captured):
            main(argv)
        return captured.getvalue()

    def test_plain_text_flag_forces_plain_output_on_wide_terminal(self) -> None:
        """--plain-text forces plain text even when terminal is wide (>72 columns)."""
        raw_markdown = "[model] rahnama-model\n\n" + self._RAHNAMA_MARKDOWN
        with patch(
            "customagenthf.zeerak.cli.shutil.get_terminal_size",
            return_value=os.terminal_size((120, 24)),
        ):
            output = self._run_main_with_mocked_feature(
                ["--feature", "rahnama", "--task", "passport", "--plain-text"],
                raw_markdown,
            )

        self.assertIn("[answer]", output)
        self.assertIn(raw_markdown, output)

    def test_markdown_flag_forces_markdown_on_narrow_terminal(self) -> None:
        """--markdown forces markdown even when terminal is narrow (≤72 columns)."""
        raw_markdown = "[model] rahnama-model\n\n" + self._RAHNAMA_MARKDOWN
        with patch(
            "customagenthf.zeerak.cli.shutil.get_terminal_size",
            return_value=os.terminal_size((40, 24)),
        ):
            output = self._run_main_with_mocked_feature(
                ["--feature", "rahnama", "--task", "passport", "--markdown"],
                raw_markdown,
            )

        self.assertIn("[answer]", output)
        self.assertIn(raw_markdown, output)

    def test_plain_text_and_markdown_are_mutually_exclusive(self) -> None:
        """--plain-text and --markdown cannot be used at the same time."""
        import subprocess
        import sys

        completed = subprocess.run(
            [sys.executable, "-m", "customagenthf", "zeerak",
             "--feature", "rahnama", "--task", "passport",
             "--plain-text", "--markdown"],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not allowed with argument", completed.stderr)

    def test_format_feature_answer_plain_mode_ignores_width(self) -> None:
        """output_mode='plain' renders plain text regardless of max_width."""
        result_wide = format_feature_answer("rahnama", self._RAHNAMA_MARKDOWN, max_width=200, output_mode=OUTPUT_MODE_PLAIN)
        result_auto_wide = format_feature_answer("rahnama", self._RAHNAMA_MARKDOWN, max_width=200, output_mode=OUTPUT_MODE_AUTO)

        self.assertNotIn("##", result_wide)
        self.assertIn("##", result_auto_wide)

    def test_format_feature_answer_markdown_mode_ignores_width(self) -> None:
        """output_mode='markdown' renders markdown regardless of max_width."""
        result_narrow = format_feature_answer("rahnama", self._RAHNAMA_MARKDOWN, max_width=40, output_mode=OUTPUT_MODE_MARKDOWN)
        result_auto_narrow = format_feature_answer("rahnama", self._RAHNAMA_MARKDOWN, max_width=40, output_mode=OUTPUT_MODE_AUTO)

        self.assertIn("##", result_narrow)
        self.assertNotIn("##", result_auto_narrow)

    def test_help_output_mentions_plain_text_and_markdown(self) -> None:
        """--help output documents both new flags."""
        import subprocess
        import sys

        completed = subprocess.run(
            [sys.executable, "-m", "customagenthf", "zeerak", "--help"],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--plain-text", completed.stdout)
        self.assertIn("--markdown", completed.stdout)


# ---------------------------------------------------------------------------
# Structured response schemas
# ---------------------------------------------------------------------------


class RahnamaResponseSchemaTests(unittest.TestCase):
    def _sample_markdown(self) -> str:
        return (
            "## Likely Purpose\n"
            "Renewing a passport.\n\n"
            "## Common Documents And Information\n"
            "- Tazkira\n"
            "- Old passport\n\n"
            "## Suggested Next Steps\n"
            "- Visit the passport office\n\n"
            "## Local Office Differences\n"
            "Processing times vary by province.\n\n"
            "## Verification Note\n"
            "Always verify with the relevant office."
        )

    def test_parse_rahnama_response_extracts_all_sections(self) -> None:
        response = parse_rahnama_response(self._sample_markdown())

        self.assertEqual(response.likely_purpose, "Renewing a passport.")
        self.assertIn("Tazkira", response.common_documents)
        self.assertIn("Visit the passport office", response.next_steps)
        self.assertIn("vary by province", response.local_differences)
        self.assertIn("verify with the relevant office", response.verification_note)

    def test_parse_rahnama_response_raw_preserves_original(self) -> None:
        md = self._sample_markdown()
        response = parse_rahnama_response(md)

        self.assertEqual(response.raw, md)

    def test_parse_rahnama_response_missing_sections_return_empty(self) -> None:
        response = parse_rahnama_response("## Likely Purpose\nRenew passport.")

        self.assertEqual(response.common_documents, "")
        self.assertEqual(response.next_steps, "")
        self.assertEqual(response.local_differences, "")
        self.assertEqual(response.verification_note, "")


class TabibResponseSchemaTests(unittest.TestCase):
    def _sample_markdown(self) -> str:
        return (
            "## Risk Level\n"
            "Low.\n\n"
            "## Immediate Self-Care\n"
            "- Rest and drink fluids.\n\n"
            "## Warning Signs\n"
            "- Difficulty breathing.\n\n"
            "## When To See A Clinician\n"
            "If symptoms persist more than three days."
        )

    def test_parse_tabib_response_extracts_all_sections(self) -> None:
        response = parse_tabib_response(self._sample_markdown())

        self.assertEqual(response.risk_level, "Low.")
        self.assertIn("Rest and drink fluids", response.immediate_self_care)
        self.assertIn("Difficulty breathing", response.warning_signs)
        self.assertIn("three days", response.when_to_see_clinician)

    def test_parse_tabib_response_missing_sections_return_empty(self) -> None:
        response = parse_tabib_response("## Risk Level\nLow risk.")

        self.assertEqual(response.immediate_self_care, "")
        self.assertEqual(response.warning_signs, "")
        self.assertEqual(response.when_to_see_clinician, "")


# ---------------------------------------------------------------------------
# Feature-level formatters
# ---------------------------------------------------------------------------


class TabibFormatterTests(unittest.TestCase):
    def test_format_tabib_answer_converts_numbered_sections(self) -> None:
        raw = (
            "1. Possible risk level: Low.\n\n"
            "2. Immediate self-care:\n"
            "   - Rest and drink fluids.\n\n"
            "3. Warning signs that require urgent care:\n"
            "   - Difficulty breathing\n\n"
            "4. When to contact a clinician:\n"
            "   - If symptoms worsen."
        )

        result = format_tabib_answer(raw)

        self.assertIn("## Risk Level", result)
        self.assertIn("## Immediate Self-Care", result)
        self.assertIn("## Warning Signs", result)
        self.assertIn("## When To See A Clinician", result)
        self.assertNotIn("1. Possible risk level", result)

    def test_format_tabib_answer_normalizes_bullets(self) -> None:
        raw = "1. Possible risk level: Low.\n\n* Rest and drink fluids.\n• Visit a doctor."
        result = format_tabib_answer(raw)

        self.assertNotIn("* Rest", result)
        self.assertNotIn("• Visit", result)
        self.assertIn("- Rest", result)
        self.assertIn("- Visit", result)

    def test_format_feature_answer_applies_tabib_formatter(self) -> None:
        raw = "1. Possible risk level: Low.\n\n2. Immediate self-care:\n- Rest."
        result = format_feature_answer("tabib", raw)

        self.assertIn("## Risk Level", result)
        self.assertIn("## Immediate Self-Care", result)


class HunarFormatterTests(unittest.TestCase):
    def test_format_hunar_answer_converts_section_headings(self) -> None:
        raw = (
            "Summary:\n"
            "A motivated candidate.\n\n"
            "Key Skills:\n"
            "- Python\n"
            "- Communication\n\n"
            "Experience:\n"
            "- 2 years in data entry\n\n"
            "Recommendations:\n"
            "- Take an advanced course."
        )

        result = format_hunar_answer(raw)

        self.assertIn("## Summary", result)
        self.assertIn("## Skills", result)
        self.assertIn("## Experience", result)
        self.assertIn("## Recommendations", result)

    def test_format_feature_answer_applies_hunar_formatter(self) -> None:
        raw = "Summary:\nA motivated candidate.\n\nKey Skills:\n- Python"
        result = format_feature_answer("hunar", raw)

        self.assertIn("## Summary", result)
        self.assertIn("## Skills", result)


class EducationFormatterTests(unittest.TestCase):
    def test_format_education_answer_converts_section_headings(self) -> None:
        raw = (
            "Lesson:\n"
            "Photosynthesis converts sunlight into glucose.\n\n"
            "Examples:\n"
            "- Plants in sunlight produce oxygen.\n\n"
            "Exercises:\n"
            "1. Describe the inputs of photosynthesis.\n\n"
            "Answer Key:\n"
            "- Water, CO2, sunlight."
        )

        result = format_education_answer(raw)

        self.assertIn("## Lesson", result)
        self.assertIn("## Examples", result)
        self.assertIn("## Exercises", result)
        self.assertIn("## Answer Key", result)

    def test_format_feature_answer_applies_education_formatter(self) -> None:
        raw = "Lesson:\nPhotosynthesis basics.\n\nExercises:\n- Describe inputs."
        result = format_feature_answer("education", raw)

        self.assertIn("## Lesson", result)
        self.assertIn("## Exercises", result)


# ---------------------------------------------------------------------------
# Routing: negative signals and confidence threshold
# ---------------------------------------------------------------------------


class RoutingSignalTests(unittest.TestCase):
    def test_low_confidence_score_defaults_to_chat(self) -> None:
        """A single tag hit (score=1) below threshold should default to chat."""
        feature, reason = route_feature("I have a health question")

        self.assertEqual(feature, "chat")
        self.assertIn("below threshold", reason)

    def test_negative_signals_reduce_score(self) -> None:
        """Negative signals for a feature reduce its score relative to others.

        'coding python' should route to codekhana. 'python' is in tabib's
        routing_negative_signals, so even if tabib had some matching tag it would
        be penalised relative to codekhana which has 'python' and 'coding' as
        explicit aliases.
        """
        feature, reason = route_feature("I need Python coding help")

        self.assertEqual(feature, "codekhana")

    def test_sufficient_alias_score_above_threshold_routes_correctly(self) -> None:
        """Multiple alias hits (score >= threshold) route to the correct feature."""
        feature, reason = route_feature("I need help with my passport registration")

        self.assertEqual(feature, "rahnama")
        self.assertIn("alias hit", reason)

    def test_confidence_reason_mentions_threshold_when_below(self) -> None:
        """Reason string mentions threshold when score is below it."""
        _, reason = route_feature("I feel sick")

        self.assertIn("threshold", reason)


# ---------------------------------------------------------------------------
# Execution hardening: rate limit and transient errors
# ---------------------------------------------------------------------------


class ExecutionHardeningTests(unittest.TestCase):
    def _make_fake_agent(self, error=None, response=None):
        class FakeAgent:
            def __init__(self_inner):
                self_inner.tasks = []

            def run(self_inner, task):
                self_inner.tasks.append(task)
                if error is not None:
                    raise error
                return response or ""

        return FakeAgent()

    def test_rate_limit_error_switches_to_fallback_model(self) -> None:
        primary_agent = self._make_fake_agent(error=Exception("429 rate limit exceeded"))
        fallback_agent = self._make_fake_agent(response="Fallback rate-limit answer")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"
        ), patch(
            "customagenthf.zeerak.agents.model_fallback_id", return_value="fallback-model"
        ), patch(
            "customagenthf.zeerak.agents.build_agent", side_effect=[primary_agent, fallback_agent]
        ):
            result = run_feature("chat", "Hello")

        self.assertIn("[fallback]", result)
        self.assertIn("Rate limit reached", result)
        self.assertIn("fallback-model", result)
        self.assertIn("Fallback rate-limit answer", result)

    def test_transient_network_error_switches_to_fallback_model(self) -> None:
        primary_agent = self._make_fake_agent(error=Exception("503 service unavailable"))
        fallback_agent = self._make_fake_agent(response="Fallback transient answer")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"
        ), patch(
            "customagenthf.zeerak.agents.model_fallback_id", return_value="fallback-model"
        ), patch(
            "customagenthf.zeerak.agents.build_agent", side_effect=[primary_agent, fallback_agent]
        ):
            result = run_feature("chat", "Hello")

        self.assertIn("[fallback]", result)
        self.assertIn("Transient network error", result)
        self.assertIn("fallback-model", result)

    def test_timeout_error_is_treated_as_transient(self) -> None:
        primary_agent = self._make_fake_agent(error=Exception("read timed out"))
        fallback_agent = self._make_fake_agent(response="Timeout fallback answer")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"
        ), patch(
            "customagenthf.zeerak.agents.model_fallback_id", return_value="fallback-model"
        ), patch(
            "customagenthf.zeerak.agents.build_agent", side_effect=[primary_agent, fallback_agent]
        ):
            result = run_feature("chat", "Hello")

        self.assertIn("[fallback]", result)
        self.assertIn("Transient network error", result)


# ---------------------------------------------------------------------------
# CLI integration: auto routing, fallback notes, formatter output
# ---------------------------------------------------------------------------


class CliIntegrationTests(unittest.TestCase):
    """Deterministic end-to-end CLI tests that patch runtime calls."""

    def _run_cli_with_mocked_run_feature(self, argv: list[str], mocked_answer: str) -> str:
        captured = StringIO()
        with patch(
            "customagenthf.zeerak.cli.run_feature",
            return_value=mocked_answer,
        ), redirect_stdout(captured):
            main(argv)
        return captured.getvalue()

    def test_auto_routing_output_contains_router_line(self) -> None:
        mocked = (
            "[router] Selected feature: rahnama. Matched score 6 for rahnama from 2 alias hit(s) and 0 tag hit(s).\n\n"
            "[model] rahnama-model\n\n"
            "## Likely Purpose\nPassport renewal."
        )
        output = self._run_cli_with_mocked_run_feature(
            ["--feature", "auto", "--task", "passport registration"],
            mocked,
        )

        self.assertIn("[answer]", output)
        self.assertIn("[router] Selected feature: rahnama", output)
        self.assertIn("[model] rahnama-model", output)

    def test_fallback_note_appears_in_answer_output(self) -> None:
        mocked = (
            "[fallback] Provider denied access to primary-model. Retried with fallback-model.\n\n"
            "[model] fallback-model\n\n"
            "Fallback answer here."
        )
        output = self._run_cli_with_mocked_run_feature(
            ["--feature", "chat", "--task", "hello"],
            mocked,
        )

        self.assertIn("[fallback]", output)
        self.assertIn("[model] fallback-model", output)

    def test_rahnama_plain_text_mode_via_flag(self) -> None:
        """--plain-text flag passes output_mode=plain to run_feature."""
        with patch("customagenthf.zeerak.cli.run_feature") as mocked_run:
            mocked_run.return_value = "[model] m\n\nSome answer"
            captured = StringIO()
            with redirect_stdout(captured):
                main(["--feature", "rahnama", "--task", "passport", "--plain-text"])

        _, kwargs = mocked_run.call_args
        self.assertEqual(kwargs.get("output_mode"), "plain")

    def test_rahnama_markdown_mode_via_flag(self) -> None:
        """--markdown flag passes output_mode=markdown to run_feature."""
        with patch("customagenthf.zeerak.cli.run_feature") as mocked_run:
            mocked_run.return_value = "[model] m\n\nSome answer"
            captured = StringIO()
            with redirect_stdout(captured):
                main(["--feature", "rahnama", "--task", "passport", "--markdown"])

        _, kwargs = mocked_run.call_args
        self.assertEqual(kwargs.get("output_mode"), "markdown")

    def test_default_output_mode_is_auto(self) -> None:
        """Without flags, output_mode defaults to 'auto'."""
        with patch("customagenthf.zeerak.cli.run_feature") as mocked_run:
            mocked_run.return_value = "[model] m\n\nSome answer"
            captured = StringIO()
            with redirect_stdout(captured):
                main(["--feature", "chat", "--task", "hello"])

        _, kwargs = mocked_run.call_args
        self.assertEqual(kwargs.get("output_mode"), "auto")

    def test_tabib_formatter_output_in_cli_flow(self) -> None:
        """run_feature result with tabib sections renders correctly."""
        tabib_formatted = (
            "[model] tabib-model\n\n"
            "## Risk Level\nLow.\n\n"
            "## Immediate Self-Care\n- Rest and drink fluids.\n\n"
            "## Warning Signs\n- Difficulty breathing.\n\n"
            "## When To See A Clinician\nIf symptoms persist."
        )
        output = self._run_cli_with_mocked_run_feature(
            ["--feature", "tabib", "--task", "I have a cough"],
            tabib_formatted,
        )

        self.assertIn("[answer]", output)
        self.assertIn("## Risk Level", output)
        self.assertIn("## Warning Signs", output)


if __name__ == "__main__":
    unittest.main()

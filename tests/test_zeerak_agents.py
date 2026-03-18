import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from customagenthf.zeerak.agents import assemble_feature_task, run_feature
from customagenthf.zeerak.formatting import format_rahnama_answer, render_rahnama_plain_text
from customagenthf.zeerak.policy import RAHNAMA_SAFE_PROMPT, TABIB_SAFE_PROMPT


class FakeAgent:
    def __init__(self, response: str | None = None, error: Exception | None = None, stdout: str = "") -> None:
        self.response = response
        self.error = error
        self.stdout = stdout
        self.tasks = []

    def run(self, task: str) -> str:
        self.tasks.append(task)
        if self.stdout:
            print(self.stdout, end="")
        if self.error is not None:
            raise self.error
        return self.response or ""


class RunFeatureTests(unittest.TestCase):
    def test_assemble_feature_task_matches_expected_snapshot(self) -> None:
        expected = (
            "Prompt\n\n"
            "Execution style: When writing action code: avoid escaped triple quotes like \\\"\\\"\\\". "
            "Prefer building answers with normal strings, short paragraphs, or lists. "
            "Return practical, concise output instead of very long literal blocks.\n\n"
            "User request: Help me practice"
        )

        self.assertEqual(assemble_feature_task("Prompt", "Help me practice"), expected)

    def test_bad_request_retries_without_tool_calling(self) -> None:
        primary_agent = FakeAgent(error=Exception("400 bad request"))
        fallback_agent = FakeAgent(response="Recovered answer")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"
        ), patch(
            "customagenthf.zeerak.agents.build_agent", side_effect=[primary_agent, fallback_agent]
        ) as mocked_build_agent:
            result = run_feature("chat", "Help me practice")

        self.assertEqual(mocked_build_agent.call_args_list[0].kwargs["prefer_tool_calling"], True)
        self.assertEqual(mocked_build_agent.call_args_list[1].kwargs["prefer_tool_calling"], False)
        self.assertIn("[model] primary-model", result)
        self.assertIn("Recovered answer", result)
        self.assertEqual(
            primary_agent.tasks[0],
            assemble_feature_task("Prompt", "Help me practice"),
        )

    def test_provider_error_switches_to_fallback_model(self) -> None:
        primary_agent = FakeAgent(error=Exception("403 provider not enabled"), stdout="primary transcript\n")
        fallback_agent = FakeAgent(response="Fallback model answer", stdout="fallback transcript\n")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"
        ), patch(
            "customagenthf.zeerak.agents.model_fallback_id", return_value="fallback-model"
        ), patch(
            "customagenthf.zeerak.agents.build_agent", side_effect=[primary_agent, fallback_agent]
        ) as mocked_build_agent:
            captured_stdout = StringIO()
            with redirect_stdout(captured_stdout):
                result = run_feature("education", "Teach me algebra")

        self.assertEqual(mocked_build_agent.call_args_list[1].kwargs["model_id"], "fallback-model")
        self.assertIn("[fallback] Provider denied access to primary-model. Retried with fallback-model.", result)
        self.assertIn("[model] fallback-model", result)
        self.assertIn("Fallback model answer", result)
        self.assertNotIn("primary transcript", captured_stdout.getvalue())
        self.assertIn("fallback transcript", captured_stdout.getvalue())

    def test_tabib_safe_prompt_payload_matches_expected_snapshot(self) -> None:
        agent = FakeAgent(response="Safe answer")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Base tabib prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="tabib-model"
        ), patch("customagenthf.zeerak.agents.build_agent", return_value=agent):
            result = run_feature("tabib", "I have a mild cough")

        expected_task = assemble_feature_task(
            f"Base tabib prompt {TABIB_SAFE_PROMPT}",
            "I have a mild cough",
        )
        self.assertEqual(agent.tasks[0], expected_task)
        self.assertIn("[model] tabib-model", result)

    def test_auto_route_wrapper_matches_expected_snapshot(self) -> None:
        with patch(
            "customagenthf.zeerak.agents.route_feature",
            return_value=("codekhana", "Matched score 9 for codekhana from 3 alias hit(s) and 0 tag hit(s)."),
        ), patch(
            "customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"
        ), patch("customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"), patch(
            "customagenthf.zeerak.agents.build_agent", return_value=FakeAgent(response="Inner answer")
        ):
            result = run_feature("auto", "Help me debug Python")

        expected = (
            "[router] Selected feature: codekhana. Matched score 9 for codekhana from 3 alias hit(s) and 0 tag hit(s).\n\n"
            "[model] primary-model\n\n"
            "Inner answer"
        )
        self.assertEqual(result, expected)

    def test_rahnama_payload_includes_policy_guidance(self) -> None:
        agent = FakeAgent(response="Document guidance")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Base rahnama prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="rahnama-model"
        ), patch("customagenthf.zeerak.agents.build_agent", return_value=agent):
            result = run_feature("rahnama", "How do I renew a passport?")

        expected_task = assemble_feature_task(
            f"Base rahnama prompt {RAHNAMA_SAFE_PROMPT}",
            "How do I renew a passport?",
        )
        self.assertEqual(agent.tasks[0], expected_task)
        self.assertIn("[model] rahnama-model", result)

    def test_rahnama_answer_formatter_normalizes_sections(self) -> None:
        raw_answer = (
            "1. Likely purpose of the process: Renew a passport.\n\n"
            "2. **Common documents or information typically needed**:\n"
            "   - Tazkira\n"
            "   - Old passport\n\n"
            "3. **Suggested next steps**:\n"
            "   - Visit the passport office\n\n"
            "4. **Where local office rules may differ**:\n"
            "   - Processing times vary\n\n"
            "**Important**: Verify local requirements."
        )

        expected = (
            "## Likely Purpose\n"
            "Renew a passport.\n\n"
            "## Common Documents And Information\n"
            "- Tazkira\n"
            "- Old passport\n\n"
            "## Suggested Next Steps\n"
            "- Visit the passport office\n\n"
            "## Local Office Differences\n"
            "- Processing times vary\n\n"
            "## Verification Note\n"
            "Verify local requirements."
        )

        self.assertEqual(format_rahnama_answer(raw_answer), expected)

    def test_rahnama_answer_formatter_handles_parenthesized_numbers_and_note(self) -> None:
        raw_answer = (
            "1) Likely purpose of the process: Renew a passport.\n\n"
            "3) Suggested next steps:\n"
            "- Visit the office\n\n"
            "Note: Verify local requirements."
        )

        expected = (
            "## Likely Purpose\n"
            "Renew a passport.\n\n"
            "## Suggested Next Steps\n"
            "- Visit the office\n\n"
            "## Verification Note\n"
            "Verify local requirements."
        )

        self.assertEqual(format_rahnama_answer(raw_answer), expected)

    def test_rahnama_run_feature_formats_final_answer(self) -> None:
        raw_answer = "1. Likely purpose of the process: Renew a passport.\n\n3. **Suggested next steps**:\n   - Visit the office"
        agent = FakeAgent(response=raw_answer)

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Base rahnama prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="rahnama-model"
        ), patch("customagenthf.zeerak.agents.build_agent", return_value=agent):
            result = run_feature("rahnama", "How do I renew a passport?")

        self.assertIn("## Likely Purpose", result)
        self.assertIn("## Suggested Next Steps", result)
        self.assertNotIn("1. Likely purpose", result)

    def test_render_rahnama_plain_text_wraps_headings_and_bullets(self) -> None:
        markdown = (
            "## Likely Purpose\n"
            "Renewing a passport helps with travel and identity verification.\n\n"
            "## Suggested Next Steps\n"
            "- Visit the nearest passport office with your documents.\n"
            "- Confirm local processing times before you go."
        )

        expected = (
            "LIKELY PURPOSE\n\n"
            "Renewing a passport helps with travel and\n"
            "identity verification.\n\n"
            "SUGGESTED NEXT STEPS\n\n"
            "- Visit the nearest passport office with\n"
            "  your documents.\n"
            "- Confirm local processing times before\n"
            "  you go."
        )

        self.assertEqual(render_rahnama_plain_text(markdown, width=40), expected)

    def test_rahnama_run_feature_uses_plain_text_for_narrow_width(self) -> None:
        raw_answer = (
            "1. Likely purpose of the process: Renewing a passport helps with travel and identity verification.\n\n"
            "3. Suggested next steps:\n"
            "- Visit the nearest passport office with your documents."
        )
        agent = FakeAgent(response=raw_answer)

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Base rahnama prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="rahnama-model"
        ), patch("customagenthf.zeerak.agents.build_agent", return_value=agent):
            result = run_feature("rahnama", "How do I renew a passport?", max_width=40)

        self.assertIn("LIKELY PURPOSE", result)
        self.assertIn("SUGGESTED NEXT STEPS", result)
        self.assertNotIn("## Likely Purpose", result)

    def test_rahnama_run_feature_suppresses_agent_transcript_noise(self) -> None:
        agent = FakeAgent(
            response="1) Likely purpose of the process: Renew a passport.",
            stdout="rahnama transcript\n",
        )

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Base rahnama prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="rahnama-model"
        ), patch("customagenthf.zeerak.agents.build_agent", return_value=agent):
            captured_stdout = StringIO()
            with redirect_stdout(captured_stdout):
                result = run_feature("rahnama", "How do I renew a passport?")

        self.assertEqual(captured_stdout.getvalue(), "")
        self.assertIn("## Likely Purpose", result)

    def test_tabib_emergency_short_circuits_before_agent_build(self) -> None:
        with patch("customagenthf.zeerak.agents.build_agent") as mocked_build_agent:
            result = run_feature("tabib", "I have chest pain and severe bleeding")

        mocked_build_agent.assert_not_called()
        self.assertIn("Call local emergency services", result)


if __name__ == "__main__":
    unittest.main()
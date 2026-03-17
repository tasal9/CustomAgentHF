import unittest
from unittest.mock import patch

from customagenthf.zeerak.agents import assemble_feature_task, run_feature
from customagenthf.zeerak.policy import TABIB_SAFE_PROMPT


class FakeAgent:
    def __init__(self, response: str | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.tasks = []

    def run(self, task: str) -> str:
        self.tasks.append(task)
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
        primary_agent = FakeAgent(error=Exception("403 provider not enabled"))
        fallback_agent = FakeAgent(response="Fallback model answer")

        with patch("customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"), patch(
            "customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"
        ), patch(
            "customagenthf.zeerak.agents.model_fallback_id", return_value="fallback-model"
        ), patch(
            "customagenthf.zeerak.agents.build_agent", side_effect=[primary_agent, fallback_agent]
        ) as mocked_build_agent:
            result = run_feature("education", "Teach me algebra")

        self.assertEqual(mocked_build_agent.call_args_list[1].kwargs["model_id"], "fallback-model")
        self.assertIn("[model] fallback-model", result)
        self.assertIn("Fallback model answer", result)

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
        with patch("customagenthf.zeerak.agents.route_feature", return_value=("codekhana", "Matched 3 keyword(s) for codekhana.")), patch(
            "customagenthf.zeerak.agents.load_feature_prompt", return_value="Prompt"
        ), patch("customagenthf.zeerak.agents.model_id_for_feature", return_value="primary-model"), patch(
            "customagenthf.zeerak.agents.build_agent", return_value=FakeAgent(response="Inner answer")
        ):
            result = run_feature("auto", "Help me debug Python")

        expected = (
            "[router] Selected feature: codekhana. Matched 3 keyword(s) for codekhana.\n\n"
            "[model] primary-model\n\n"
            "Inner answer"
        )
        self.assertEqual(result, expected)

    def test_tabib_emergency_short_circuits_before_agent_build(self) -> None:
        with patch("customagenthf.zeerak.agents.build_agent") as mocked_build_agent:
            result = run_feature("tabib", "I have chest pain and severe bleeding")

        mocked_build_agent.assert_not_called()
        self.assertIn("Call local emergency services", result)


if __name__ == "__main__":
    unittest.main()
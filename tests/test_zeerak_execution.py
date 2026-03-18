import os
import unittest
from unittest.mock import patch

from customagenthf.zeerak.agents import run_feature


class FakeInferenceClientModel:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id


class FakeCodeAgent:
    instances = []

    def __init__(self, tools, model) -> None:
        self.tools = tools
        self.model = model
        self.tasks = []
        FakeCodeAgent.instances.append(self)

    def run(self, task: str) -> str:
        self.tasks.append(task)
        return f"code:{self.model.model_id}"


class FakeToolCallingAgent:
    instances = []

    def __init__(self, tools, model) -> None:
        self.tools = tools
        self.model = model
        self.tasks = []
        FakeToolCallingAgent.instances.append(self)

    def run(self, task: str) -> str:
        self.tasks.append(task)
        return f"tool:{self.model.model_id}"


class FakeDuckDuckGoSearchTool:
    pass


class ZeerakExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        FakeCodeAgent.instances = []
        FakeToolCallingAgent.instances = []

    def test_chat_feature_uses_tool_calling_agent_end_to_end(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch("customagenthf.zeerak.agents.InferenceClientModel", FakeInferenceClientModel), patch(
            "customagenthf.zeerak.agents.ToolCallingAgent", FakeToolCallingAgent
        ), patch("customagenthf.zeerak.agents.CodeAgent", FakeCodeAgent), patch(
            "customagenthf.zeerak.agents.DuckDuckGoSearchTool", FakeDuckDuckGoSearchTool
        ):
            result = run_feature("chat", "Speak in Dari")

        self.assertEqual(result, "[model] CohereForAI/aya-expanse-32b\n\ntool:CohereForAI/aya-expanse-32b")
        self.assertEqual(len(FakeToolCallingAgent.instances), 1)
        self.assertEqual(len(FakeCodeAgent.instances), 0)
        self.assertIn("Zeerak Chat", FakeToolCallingAgent.instances[0].tasks[0])

    def test_dehqan_feature_uses_search_enabled_code_agent_end_to_end(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch("customagenthf.zeerak.agents.InferenceClientModel", FakeInferenceClientModel), patch(
            "customagenthf.zeerak.agents.ToolCallingAgent", FakeToolCallingAgent
        ), patch("customagenthf.zeerak.agents.CodeAgent", FakeCodeAgent), patch(
            "customagenthf.zeerak.agents.DuckDuckGoSearchTool", FakeDuckDuckGoSearchTool
        ):
            result = run_feature("dehqan", "Wheat irrigation advice")

        self.assertEqual(result, "[model] meta-llama/Llama-3.3-70B-Instruct\n\ncode:meta-llama/Llama-3.3-70B-Instruct")
        self.assertEqual(len(FakeCodeAgent.instances), 1)
        self.assertEqual(len(FakeCodeAgent.instances[0].tools), 1)
        self.assertIsInstance(FakeCodeAgent.instances[0].tools[0], FakeDuckDuckGoSearchTool)
        self.assertIn("Dehqan AI", FakeCodeAgent.instances[0].tasks[0])

    def test_rahnama_feature_routes_and_runs_end_to_end(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch("customagenthf.zeerak.agents.InferenceClientModel", FakeInferenceClientModel), patch(
            "customagenthf.zeerak.agents.ToolCallingAgent", FakeToolCallingAgent
        ), patch("customagenthf.zeerak.agents.CodeAgent", FakeCodeAgent), patch(
            "customagenthf.zeerak.agents.DuckDuckGoSearchTool", FakeDuckDuckGoSearchTool
        ):
            result = run_feature("auto", "How do I apply for a passport document?")

        self.assertIn("[router] Selected feature: rahnama.", result)
        self.assertIn("[model] meta-llama/Llama-3.1-70B-Instruct", result)
        self.assertIn("code:meta-llama/Llama-3.1-70B-Instruct", result)
        self.assertIn("Rahnama", FakeCodeAgent.instances[0].tasks[0])
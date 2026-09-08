import unittest
import copy
from unittest.mock import patch

import starlite_agent as agent
from starlite_brain import StarliteBrain


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class StarliteAgentTests(unittest.TestCase):
    def test_repository_boundaries(self):
        self.assertEqual(agent.read_file("Modelfile")["path"], "Modelfile")
        with self.assertRaises(ValueError):
            agent.read_file("../outside.txt")
        with self.assertRaises(ValueError):
            agent.run_shell("git commit")
        with self.assertRaises(ValueError):
            agent.run_shell("python3 -c print(1)")

    @patch("starlite_agent.requests.post")
    def test_tool_call_round_trip(self, post):
        captured_messages = []

        def capture_request(*args, **kwargs):
            captured_messages.append(copy.deepcopy(kwargs["json"]["messages"]))
            return [
                FakeResponse({"message": {"role": "assistant", "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": "Modelfile"}}}]}}),
                FakeResponse({"message": {"role": "assistant", "content": "The model file is present."}}),
            ][len(captured_messages) - 1]

        post.side_effect = capture_request
        result = agent.StarliteAgent().chat("Check the model file")
        self.assertEqual(result, "The model file is present.")
        self.assertEqual(captured_messages[1][-1]["role"], "tool")

    @patch("starlite_agent.requests.post")
    def test_json_string_arguments_are_supported(self, post):
        post.side_effect = [
            FakeResponse({"message": {"tool_calls": [{"function": {"name": "list_directory", "arguments": '{"path": "."}'}}]}}),
            FakeResponse({"message": {"content": "Listed."}}),
        ]
        self.assertEqual(agent.StarliteAgent().chat("List the root"), "Listed.")

    @patch("starlite_agent.requests.post")
    def test_ollama_failure_is_actionable(self, post):
        post.side_effect = agent.requests.ConnectionError("offline")
        with self.assertRaisesRegex(RuntimeError, "Start Ollama"):
            agent.StarliteAgent().chat("hello")

    @patch("starlite_brain.StarliteAgent")
    def test_custom_brain_persists_device_state(self, agent_class):
        fake_agent = agent_class.return_value
        fake_agent.chat.return_value = "STARLITE response"
        with self.subTest("portable identity"):
            import tempfile
            with tempfile.TemporaryDirectory() as directory:
                brain = StarliteBrain(device_id="samsung-galaxy-tab-a9-plus", memory_path=f"{directory}/state.json")
                brain.remember("shared design decision", memory_type="semantic")
                brain.remember("felt hopeful", memory_type="emotional")
                self.assertEqual(brain.chat("continue"), "STARLITE response")
                restored = StarliteBrain(device_id="motorola-razr-2025", memory_path=f"{directory}/state.json", agent=fake_agent)
                self.assertEqual(restored.export_state()["memories"][0]["note"], "shared design decision")
                self.assertEqual(restored.recall("emotional")[0]["note"], "felt hopeful")


if __name__ == "__main__":
    unittest.main()
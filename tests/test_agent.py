import tempfile
import unittest
from pathlib import Path

from mycodex.agents.agent import Agent
from mycodex.llm.tests.fake import FakeModelClient
from mycodex.models import ExecutionContext, ModelResponse
from mycodex.tools.apply_patch import apply_patch_spec, execute_apply_patch
from mycodex.tools.registry import ToolRegistry


class AgentTests(unittest.TestCase):
    def test_agent_returns_final_text_after_a_custom_tool_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ToolRegistry()
            registry.register(
                "apply_patch",
                apply_patch_spec,
                execute_apply_patch,
            )

            model = FakeModelClient(
                responses=[
                    ModelResponse(
                        output=[
                            {
                                "type": "custom_tool_call",
                                "call_id": "call_1",
                                "name": "apply_patch",
                                "input": (
                                    "*** Begin Patch\n"
                                    "*** Add File: hello.txt\n"
                                    "+Hello from Agent\n"
                                    "*** End Patch"
                                ),
                            }
                        ]
                    ),
                    ModelResponse(
                        output=[
                            {
                                "type": "message",
                                "role": "assistant",
                                "content": [
                                    {
                                        "type": "output_text",
                                        "text": "The file was created.",
                                    }
                                ],
                            }
                        ]
                    ),
                ]
            )

            agent = Agent(
                model_client=model,
                tool_registry=registry,
                context=ExecutionContext(
                    workspace_root=root,
                    cwd=root,
                ),
            )

            result = agent.run(
                {
                    "type": "input_text",
                    "text": "Create hello.txt",
                }
            )

            self.assertEqual(result["text"], "The file was created.")
            self.assertEqual(
                (root / "hello.txt").read_text(encoding="utf-8"),
                "Hello from Agent\n",
            )
            self.assertEqual(
                [item["type"] for item in agent.history],
                [
                    "message",
                    "custom_tool_call",
                    "custom_tool_call_output",
                    "message",
                ],
            )


if __name__ == "__main__":
    unittest.main()

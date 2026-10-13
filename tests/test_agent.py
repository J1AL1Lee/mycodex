import tempfile
import unittest
from pathlib import Path
from mycodex.agents.agent import Agent, MaxTurnExceeded
from mycodex.llm.tests.fake import FakeModelClient
from mycodex.models import ExecutionContext, ModelResponse, ToolCall
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
def execute_fake(
    call: ToolCall,
    context: ExecutionContext,
) -> str:
    return "handler excuted"
class MaxTurnTests(unittest.TestCase):
    def test_agent_stops_after_max_turn(self) -> None:
        # ---- Arrange ----
        # 1. 一个什么都不做的工具。handler 的签名是 (call, context) -> str
        registry = ToolRegistry()
        registry.register("echo", {"type": "function", "name": "echo"}, execute_fake)

        # 2. 一个"永远在调工具"的假模型
        tool_call = ModelResponse(
            output=[
                {
                    "type": "function_call",
                    "call_id": "call_1",
                    "name": "echo",
                    "arguments": "{}",
                }
            ]
        )
        model = FakeModelClient(responses=[tool_call] * 10)

        # 3. Agent：max_turn 设得比 10 小
        root = Path(tempfile.gettempdir())
        agent = Agent(
            model_client=model,
            tool_registry=registry,
            context=ExecutionContext(workspace_root=root, cwd=root),
            max_turn=3,
        )

        # ---- Act + Assert ----
        with self.assertRaises(MaxTurnExceeded):
            agent.run({"type": "input_text", "text": "loop forever"})

        # 模型应该恰好被调用了几次？
        self.assertEqual(model.index, 3)
if __name__ == "__main__":
    unittest.main()

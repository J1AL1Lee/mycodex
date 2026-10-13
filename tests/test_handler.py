import tempfile
import unittest
from pathlib import Path
from mycodex.agents.agent import Agent, MaxTurnExceeded
from mycodex.llm.tests.fake import FakeModelClient
from mycodex.models import ExecutionContext, ModelResponse, ToolCall
from mycodex.tools.apply_patch import apply_patch_spec, execute_apply_patch
from mycodex.tools.registry import ToolRegistry


def execute_broken(
    call: ToolCall,
    context: ExecutionContext,
) -> str:
    raise RuntimeError("This is a handler error")  # 随便写一句报错信息


class ToolErrorTests(unittest.TestCase):
    def test_tool_error_is_returned_to_the_model(self) -> None:
        # ---- Arrange ----
        registry = ToolRegistry()
        registry.register("echo", {"type": "function", "name": "echo"}, execute_broken)

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

        Msg = ModelResponse(
            output=[
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "The is a assistant message.",
                        }
                    ],
                }
            ]
        )
        # 假模型要准备两轮回复：
        #   第 1 轮：调用 echo 工具（参照任务 1 里的 tool_call 怎么写）
        #   第 2 轮：回复一段文字（参照第一个测试里的 message 怎么写）
        model = FakeModelClient(responses=[tool_call, Msg])

        root = Path(tempfile.gettempdir())
        agent = Agent(
            model_client=model,
            tool_registry=registry,
            context=ExecutionContext(workspace_root=root, cwd=root),
        )

        # ---- Act ----
        result = agent.run({"type": "input_text", "text": "try the tool"})

        # ---- Assert ----
        # 1. run() 正常返回了第 2 轮的文字
        self.assertEqual(result["text"], "The is a assistant message.")

        # 2. history 里那条工具 output 包含了报错信息
        #    history 的顺序：[0] 用户消息  [1] 工具调用  [2] 工具 output  [3] 模型回复
        tool_output = agent.history[2]
        self.assertIn("This is a handler error", tool_output["output"])

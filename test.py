from .agents.agent import Agent
from .tools.registry import ToolRegistry
from .tools.shell import execute_shell, shell_spec
from pathlib import Path
from .types import ExecutionContext, ModelResponse, ResponseItem, ToolSpec
from .llm.base import ModelClient, ModelResponse, ResponseItem, ToolSpec
import os

from .llm.deepseek import DeepSeekModelClient
registry = ToolRegistry()
registry.register("shell", shell_spec, execute_shell)

context = ExecutionContext(
    workspace_root=Path(r"D:\codex\mycodex"),
    cwd=Path(r"D:\codex\mycodex"),
)

model = DeepSeekModelClient(
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

agent = Agent(
    model_client=model,
    tool_registry=registry,
    context=context,
)
result = agent.run(
    {
        "type": "input_text",
        "text": "Please execute the command 'echo Hello World' in the shell.",
    }
)
print(result)
print(agent.history)

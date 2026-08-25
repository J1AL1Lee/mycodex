from ..llm.base import ModelClient
from ..types import ModelResponse, ResponseItem, ToolSpec
from abc import ABC, abstractmethod
from typing import Any, List
from ..tools.registry import ToolRegistry
from ..types import ToolCall, ToolCallOutput, ExecutionContext
from ..types import FunctionCallOutput, CustomToolCallOutput
from ..llm.tests.fake import FakeModelClient
from ..types import MessageContent, ToolOutputContent
from ..types import UserMessage, OutputText, InputText

class Agent:
    history: List[ResponseItem]
    
    def __init__(self, model_client: ModelClient, tool_registry: ToolRegistry, context: ExecutionContext):
        self.model_client = model_client
        self.tool_registry = tool_registry
        self.context = context
        self.history: list[ResponseItem] = []

    def run(self, userMsg: InputText) -> OutputText:
        # Append user message to history
        self.history.append(UserMessage(type="message", role="user", content=[userMsg]))
        loop_condition: bool = False
        while not loop_condition:
            # Generate model response
            loop_condition = True
            model_response: ModelResponse = self.model_client.generate(self.history, self.tool_registry.specs())
            
            for output in model_response.output:
                if output["type"] == "message":
                    self.history.append(output)
                    result = OutputText(type="output_text", text=output["content"][0]["text"])
                elif output["type"] in ["function_call", "custom_tool_call"]:
                    self.history.append(output)
                    tool_output = self.tool_registry.execute(output, self.context)
                    self.history.append(tool_output)
                    loop_condition = False
        return result
            
            
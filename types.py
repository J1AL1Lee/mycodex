from typing import Any, Literal, NotRequired, TypedDict
from dataclasses import dataclass
from pathlib import Path

ToolSpec = dict[str, Any]
# content
class InputText(TypedDict):
    type: Literal["input_text"]
    text: str

class OutputText(TypedDict):
    type: Literal["output_text"]
    text: str

MessageContent = InputText | OutputText
ToolOutputContent = InputText
ToolCall = FunctionCall | CustomToolCall
ToolCallOutput = FunctionCallOutput | CustomToolCallOutput

# 用户文本
class UserMessage(TypedDict) :
    type : Literal["message"]
    role : Literal["user"]
    content : list[InputText]

# Assistant 文本
class AssistantMessage(TypedDict):
    type : Literal["message"]
    role : Literal["assistant"]
    content : list[OutputText]

# function tool call
class FunctionCall(TypedDict):
    type : Literal["function_call"]
    call_id : str
    name : str
    arguments : str

# custom/freeform tool call
class CustomToolCall(TypedDict):
    type : Literal["custom_tool_call"]
    call_id: str
    name: str
    input: str

# tool result
class FunctionCallOutput(TypedDict):
    type: Literal["function_call_output"]
    call_id: str
    output: str | list[ToolOutputContent]

class CustomToolCallOutput(TypedDict):
    type: Literal["custom_tool_call_output"]
    call_id: str
    output: str | list[ToolOutputContent]

class ReasoningItem(TypedDict):
    type: Literal["reasoning"]
    id: NotRequired[str]
    summary: list[Any]
    content: NotRequired[list[Any]]
    encrypted_content: NotRequired[str | None]

# ResponseItem总类型
ResponseItem = (
    UserMessage
    | AssistantMessage
    | FunctionCall
    | CustomToolCall
    | FunctionCallOutput
    | CustomToolCallOutput
    | ReasoningItem
)
# Execution Context
@dataclass(frozen=True, slots=True)
class ExecutionContext:
    workspace_root: Path
    cwd: Path
    timeout_ms: int = 10_000
    max_output_bytes: int = 50_000

# Model
ModelOutputItem = (
    AssistantMessage
    | ReasoningItem
    | FunctionCall
    | CustomToolCall
)
@dataclass
class ModelResponse:
    output: list[ModelOutputItem]


from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, NotRequired, TypedDict


ToolSpec = dict[str, Any]


class InputText(TypedDict):
    type: Literal["input_text"]
    text: str


class OutputText(TypedDict):
    type: Literal["output_text"]
    text: str


MessageContent = InputText | OutputText
ToolOutputContent = InputText


class UserMessage(TypedDict):
    type: Literal["message"]
    role: Literal["user"]
    content: list[InputText]


class AssistantMessage(TypedDict):
    type: Literal["message"]
    role: Literal["assistant"]
    content: list[OutputText]


class FunctionCall(TypedDict):
    type: Literal["function_call"]
    call_id: str
    name: str
    arguments: str


class CustomToolCall(TypedDict):
    type: Literal["custom_tool_call"]
    call_id: str
    name: str
    input: str


class FunctionCallOutput(TypedDict):
    type: Literal["function_call_output"]
    call_id: str
    output: str | list[ToolOutputContent]


class CustomToolCallOutput(TypedDict):
    type: Literal["custom_tool_call_output"]
    call_id: str
    output: str | list[ToolOutputContent]


ToolCall = FunctionCall | CustomToolCall
ToolCallOutput = FunctionCallOutput | CustomToolCallOutput


class ReasoningItem(TypedDict):
    type: Literal["reasoning"]
    id: NotRequired[str]
    summary: list[Any]
    content: NotRequired[list[Any]]
    encrypted_content: NotRequired[str | None]


ResponseItem = (
    UserMessage
    | AssistantMessage
    | FunctionCall
    | CustomToolCall
    | FunctionCallOutput
    | CustomToolCallOutput
    | ReasoningItem
)


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    workspace_root: Path
    cwd: Path
    timeout_ms: int = 10_000
    max_output_bytes: int = 50_000


ModelOutputItem = AssistantMessage | ReasoningItem | FunctionCall | CustomToolCall


@dataclass
class ModelResponse:
    output: list[ModelOutputItem]

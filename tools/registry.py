from collections.abc import Callable

from ..models import (
    ToolSpec,
    ExecutionContext,
    FunctionCallOutput,
    CustomToolCallOutput,
    ToolCall,
    ToolCallOutput,
)

ToolHandler = Callable[[ToolCall, ExecutionContext], str]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, tuple[ToolSpec, ToolHandler]] = {}

    def register(
        self,
        name: str,
        spec: ToolSpec,
        handler: ToolHandler,
    ) -> None:
        self._tools[name] = (spec, handler)

    def specs(self) -> list[ToolSpec]:
        return [spec for spec, _ in self._tools.values()]

    def get_handler(self, name: str) -> ToolHandler:
        return self._tools[name][1]

    def execute(
        self,
        call: ToolCall,
        context: ExecutionContext,
    ) -> ToolCallOutput:
        tool = self._tools.get(call["name"])

        if tool is None:
            result = f"Unknown tool: {call['name']}"
        else:
            handler = tool[1]
            result = handler(call, context)

        if call["type"] == "function_call":
            return FunctionCallOutput(
                type="function_call_output",
                call_id=call["call_id"],
                output=result,
            )

        return CustomToolCallOutput(
            type="custom_tool_call_output",
            call_id=call["call_id"],
            output=result,
        )

from collections.abc import Callable

from dataclasses import dataclass

from ..types import (
    ToolSpec,
    ExecutionContext,
    ToolCall,
    ToolCallOutput,
    )  

ToolHandler = Callable[..., str]

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
        return [
            spec 
            for spec, _ in self._tools.values()
        ]

    def get_handler(self, name: str) -> ToolHandler:
        return self._tools[name][1]

    def execution(
            self,
            call: ToolCall,
            context: ExecutionContext,
    )-> ToolCallOutput:
        if call.name not in self._tools:
           if call.type == function_call: 
               return ToolCallOutput("function_call_output", call.call_id, "Unknown tool: {call.name}")
           else: return ToolCallOutput("custom_tool_call_output", call.call_id, "Unknown tool: {call.name}")
        else:
            handler = _tools[call.name][1]
            
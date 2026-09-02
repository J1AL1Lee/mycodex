from ..llm.base import ModelClient
from ..models import (
    ExecutionContext,
    InputText,
    ModelResponse,
    OutputText,
    ResponseItem,
    UserMessage,
)
from ..tools.registry import ToolRegistry

class Agent:
    def __init__(
        self,
        model_client: ModelClient,
        tool_registry: ToolRegistry,
        context: ExecutionContext,
    ):
        self.model_client = model_client
        self.tool_registry = tool_registry
        self.context = context
        self.history: list[ResponseItem] = []

    def run(self, user_message: InputText) -> OutputText:
        self.history.append(
            UserMessage(type="message", role="user", content=[user_message])
        )

        while True:
            model_response: ModelResponse = self.model_client.generate(
                self.history,
                self.tool_registry.specs(),
            )
            final_text: OutputText | None = None
            called_a_tool = False

            for output in model_response.output:
                if output["type"] == "message":
                    self.history.append(output)
                    for content_item in output["content"]:
                        if content_item["type"] == "output_text":
                            final_text = OutputText(
                                type="output_text",
                                text=content_item["text"],
                            )

                elif output["type"] in {"function_call", "custom_tool_call"}:
                    self.history.append(output)
                    self.history.append(
                        self.tool_registry.execute(output, self.context)
                    )
                    called_a_tool = True

            if called_a_tool:
                continue

            if final_text is not None:
                return final_text

            raise RuntimeError("Model response contained neither a tool call nor text.")

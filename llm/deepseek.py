from typing import cast

from openai import OpenAI

from .base import ModelClient
from ..models import (
    ModelOutputItem,
    ModelResponse,
    ResponseItem,
    ToolSpec,
)


class DeepSeekModelClient(ModelClient):
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-v4-flash",
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = model

    def generate(
        self,
        history: list[ResponseItem],
        tool_space: list[ToolSpec],
    ) -> ModelResponse:
        response = self.client.responses.create(
            model=self.model,
            input=history,
            tools=tool_space,
            reasoning={"effort": "none"},
            max_output_tokens=1024,
        )

        output = [
            item.model_dump(exclude_none=True)
            for item in response.output
        ]

        return ModelResponse(
            output=cast(list[ModelOutputItem], output)
        )

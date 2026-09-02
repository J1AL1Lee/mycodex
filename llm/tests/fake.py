from ..base import ModelClient
from ...models import ModelResponse, ResponseItem, ToolSpec

class FakeModelClient(ModelClient):
    def __init__(self, responses: list[ModelResponse]):
        self.responses = responses
        self.index = 0

    def generate(
        self,
        history: list[ResponseItem],
        tool_space: list[ToolSpec],
    ) -> ModelResponse:
        response = self.responses[self.index]
        self.index += 1
        return response

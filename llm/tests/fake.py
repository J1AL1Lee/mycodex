from ..base import ModelClient
from ...types import ModelResponse

class FakeModelClient(ModelClient):
    def __init__(self, responses: list[ModelResponse]):
        self.responses = responses
        self.index = 0

    def generate(self, history, tool_space)->ModelResponse:
        responses = self.responses[self.index]
        self.index += 1
        return responses

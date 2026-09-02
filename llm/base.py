from ..models import ModelResponse, ResponseItem, ToolSpec
from abc import ABC, abstractmethod

class ModelClient(ABC):
    @abstractmethod
    def generate(
            self,
            history: list[ResponseItem],
            tool_space: list[ToolSpec],
    ) -> ModelResponse:
        ...


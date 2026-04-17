from abc import ABC, abstractmethod
from typing import List


class IModel(ABC):
    """Interface for model usage class"""

    @abstractmethod
    def __init__(self, model_name: str, device_map: str = "auto") -> None:
        pass

    @abstractmethod
    def __call__(self, prompts: List[str], max_new_tokens: int = 512) -> List[str]:
        pass

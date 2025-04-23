from abc import ABC, abstractmethod


class IModel(ABC):
    """Interface for model usage class"""

    @abstractmethod
    def __init__(self, model_name, device_map="auto"):
        pass

    @abstractmethod
    def __call__(self, prompts, max_new_tokens=512):
        pass

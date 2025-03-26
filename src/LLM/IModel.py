from abc import ABC, abstractmethod


class IModel(ABC):
    @abstractmethod
    def __init__(self, model_name, device_map="auto"):
        pass

    @abstractmethod
    def generate(self, prompt, max_new_tokens=512, return_full_text=False):
        pass
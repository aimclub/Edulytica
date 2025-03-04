from enum import Enum
from transformers import pipeline


class Models(str, Enum):
    QDS1 = "Megnis/results_modified"
    LL1 = "Megnis/qdora"


class LLMWrapper:
    def __init__(self, model: Models):
        model_path = f"{model.value}"
        self.generator = pipeline("text-generation", model=model_path)

    def send_request(self, prompt: str, **kwargs) -> list:
        return self.generator(prompt, **kwargs)

    def process_response(self, response: list) -> str:
        return response[0]['generated_text']

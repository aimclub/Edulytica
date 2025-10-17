from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.models.llm import IModel
from src.models.llm import DEFAULT_SYSTEM_PROMPT


class ModelPipeline(IModel):
    def __init__(self, model_name: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT, device_map: str = "auto") -> None:
        """Class for Vikhr-Nemo instruct usage. For inference using huggingface transformers pipeline"""

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map)
        self.system_prompt = system_prompt

    def __call__(self, prompts: List[str], max_new_tokens: int = 512, return_full_text: bool = False) -> List[str]:
        """Method for text generation by model.
        Takes list of prompts1 and max new tokens and return list with model generated text."""
        task = "text-generation"
        self.pipeline = pipeline(
            task,
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=max_new_tokens,
            return_full_text=return_full_text
        )
        prompts = [self.system_prompt + prompt for prompt in prompts]
        return self.pipeline(prompts)

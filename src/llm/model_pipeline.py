from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.llm import IModel
from src.llm import DEFAULT_SYSTEM_PROMPT


class ModelPipeline(IModel):
    def __init__(self, model_name, system_prompt=DEFAULT_SYSTEM_PROMPT, device_map="auto"):
        """Class for Vikhr-Nemo instruct usage. For inference using huggingface transformers pipeline"""

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map)
        self.system_prompt = system_prompt

    def __call__(self, prompts: list, max_new_tokens=512, return_full_text=False):
        """Method for text generation by model.
        Takes list of prompts and max new tokens and return list with model generated text."""
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

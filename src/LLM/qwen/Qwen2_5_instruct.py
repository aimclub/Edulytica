from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, pipeline
from src.LLM import IModel


class Qwen2_5_instruct(IModel):
    """Class for Qwen2.5 instruct usage"""

    def __init__(self, model_name=None, device_map="auto"):
        if model_name is None:
            model_name = "RefalMachine/ruadapt_qwen2.5_7B_ext_u48_instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map)
        self.device = self.model.device

    def generate(self, prompts: list, max_new_tokens=512):
        """Method for text generation by model.
        Takes list of prompts and max new tokens and return list with model generated text"""
        generation_config = GenerationConfig(max_new_tokens=max_new_tokens)
        model_inputs = self.tokenizer(prompts, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**model_inputs, generation_config=generation_config)
        response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return response


class Qwen2_5_instruct_pipline(IModel):
    def __init__(self, model_name=None, device_map="auto"):
        if model_name is None:
            model_name = "RefalMachine/ruadapt_qwen2.5_7B_ext_u48_instruct"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map)

    def generate(self, prompts: list, max_new_tokens=512, return_full_text=False):
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
        return self.pipeline(prompts)

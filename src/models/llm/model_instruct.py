from typing import List, Dict, Optional, Callable
import torch
from src.models.llm import IModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
from src.models.llm import DEFAULT_SYSTEM_PROMPT
from src.models.llm.exceptions.quantization_exception import QuantizationException


ChatTemplateFunc = Callable[[str], List[Dict[str, str]]]


class ModelInstruct(IModel):
    def __init__(
            self,
            model_name: str,
            chat_template: ChatTemplateFunc,
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            device_map: str = "auto",
            quantization: Optional[str] = None,
            bnb_4bit_quant_type: str = "nf4",
            bnb_4bit_use_double_quant: bool = True) -> None:
        """To use quantization model pass argument quantization='4bit'
        to load in 4bit or quantization='8bit' to load in 8bit"""

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        bnb_config = None

        if quantization == "8bit":
            bnb_config = BitsAndBytesConfig(load_in_8bit=True)
        elif quantization == "4bit":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=bnb_4bit_use_double_quant)
        elif quantization is not None:
            raise QuantizationException
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map,
                                                          quantization_config=bnb_config,
                                                          torch_dtype=torch.float16)
        self.device = self.model.device
        self.system_prompt = system_prompt
        self.chat_template = chat_template

    def apply_chat_template(self, system_prompt: str, prompts: List[str]) -> List[str]:
        """Method for applying chat template"""
        messages = list()
        for prompt in prompts:
            messages.append(self.chat_template(prompt))
        texts = list(map(lambda message: self.tokenizer.apply_chat_template(
            message, tokenize=False, add_generation_prompt=True), messages))
        return texts

    def __call__(self, prompts: List[str], max_new_tokens: int = 512) -> List[str]:
        """Method for text generation by model.
        Takes list of prompts1 and max new tokens and return list with model generated text"""
        generation_config = GenerationConfig(max_new_tokens=max_new_tokens)

        texts = self.apply_chat_template(self.system_prompt, prompts)
        model_inputs = self.tokenizer(texts, return_tensors="pt").to(self.device)

        input_ids_len = model_inputs["input_ids"].shape[-1]
        outputs = self.model.generate(**model_inputs, generation_config=generation_config)
        new_tokens = outputs[:, input_ids_len:]
        response = self.tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
        return response

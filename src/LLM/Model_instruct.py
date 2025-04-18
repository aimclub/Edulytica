from src.LLM import IModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from src.LLM import DEFAULT_SYSTEM_PROMPT


class Model_instruct(IModel):
    def __init__(
            self,
            model_name,
            chat_template,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            device_map="auto"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map)
        self.device = self.model.device
        self.system_prompt = system_prompt
        self.chat_template = chat_template

    def apply_chat_template(self, system_prompt: str, prompts: list):
        """Method for applying chat template"""
        messages = list()
        for prompt in prompts:
            messages.append(self.chat_template(prompt))
        texts = list(map(lambda message: self.tokenizer.apply_chat_template(
            message, tokenize=False, add_generation_prompt=True), messages))
        return texts

    def __call__(self, prompts: list, max_new_tokens=512):
        """Method for text generation by model.
        Takes list of prompts and max new tokens and return list with model generated text"""
        generation_config = GenerationConfig(max_new_tokens=max_new_tokens)

        texts = self.apply_chat_template(self.system_prompt, prompts)
        model_inputs = self.tokenizer(texts, return_tensors="pt").to(self.device)

        outputs = self.model.generate(**model_inputs, generation_config=generation_config)
        response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return response

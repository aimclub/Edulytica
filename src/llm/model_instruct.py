from src.llm import model_interface
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
from src.llm import DEFAULT_SYSTEM_PROMPT
from src.exeptions.llm.quantization_exeption import QuantizationExeption


class Model_instruct(model_interface):
    def __init__(
            self,
            model_name,
            chat_template,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            device_map="auto",
            quantization=None,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True):
        """To use quantization model pass argument quantization='4bit' to load in 4bit or quantization='8bit' to load in 8bit"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        bnb_config = None

        if quantization == "8bit":
            bnb_config = BitsAndBytesConfig(load_in_8bit=True)
        elif quantization == "4bit":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=bnb_4bit_use_double_quant)
        else:
            raise QuantizationExeption
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map,
                                                          quantization_config=bnb_config)
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

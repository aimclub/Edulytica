import os, torch, logging
from peft import PeftModel, PeftConfig, LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig, pipeline

# DEFAULT_MESSAGE_TEMPLATE = "<|start_header_id|>{role}<|end_header_id|>{content}<|eot_id|>"
# DEFAULT_RESPONSE_TEMPLATE = "<|begin_of_text|>"
# DEFAULT_SYSTEM_PROMPT = "Ты опытный преподаватель университета, твоя задача делать суммаризацию научных текстов.\n Суммаризируй часть научной работы, сохрани основные пункты, главные факты, термины и выводы. Твой ответ должен быть кратким, содержать от 10 до 15 предложений. Не добавляй в ответ ничего от себя, опирайся только на исходный текст. Вот научный текст для суммаризации:"

class Conversation:
    def __init__(
        self,
        message_template,
        system_prompt,
        response_template
    ):
        self.message_template = message_template
        self.response_template = response_template
        self.messages = [{
            "role": "system",
            "content": system_prompt
        }]

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_bot_message(self, message):
        self.messages.append({
            "role": "bot",
            "content": message
        })

    def get_prompt(self, tokenizer):
        final_text = self.response_template
        for message in self.messages:
            message_text = self.message_template.format(**message)
            final_text += message_text
        return final_text.strip()

class LLM():
    def __init__(self, model_name, adapter_name):
        self.model_name = model_name
        self.adapter_name = adapter_name
        self.quant_config = BitsAndBytesConfig(
             load_in_4bit=True,
             bnb_4bit_quant_type="nf4",
             bnb_4bit_compute_dtype=torch.float16,
             bnb_4bit_use_double_quant=False
        )
        self.model = PeftModel.from_pretrained(
            AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=self.quant_config,
                torch_dtype=torch.float16,
                device_map='auto'
            ), self.adapter_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        self.generation_config = GenerationConfig.from_pretrained(self.model_name)

    def generate(self, prompt):
        data = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        data = {k: v.to(self.model.device) for k, v in data.items()}
        output_ids = self.model.generate(
            **data,
            generation_config=self.generation_config
        )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = self.tokenizer.decode(output_ids, skip_special_tokens=True)
        return output.strip()

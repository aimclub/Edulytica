from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from src.LLM import Model_instruct
from src.LLM import DEFAULT_SYSTEM_PROMPT


class Qwen2_5_instruct(Model_instruct):
    """Class for Qwen2.5 instruct usage. For inference using huggingface transformers"""

    def __init__(
            self,
            model_name=None,
            chat_template=None,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            device_map="auto",
            quantization=None,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
    ):
        if model_name is None:
            model_name = "RefalMachine/ruadapt_qwen2.5_7B_ext_u48_instruct"
        if chat_template is None:
            chat_template = lambda prompt: [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        super().__init__(
            model_name,
            chat_template,
            system_prompt,
            device_map,
            quantization,
            bnb_4bit_quant_type,
            bnb_4bit_use_double_quant)


if __name__ == "__main__":
    model = Qwen2_5_instruct(quantization="8bit")
    print(model.device)
    print(model("Привет!"))

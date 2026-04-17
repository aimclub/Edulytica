from typing import Optional

from src.models.llm import ModelInstruct, ChatTemplateFunc
from src.models.llm import DEFAULT_SYSTEM_PROMPT


class VikhrNemoInstruct(ModelInstruct):
    """Class for Vikhr-Nemo instruct usage. For inference using huggingface transformers"""

    def __init__(
            self,
            model_name: str = "Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24",
            chat_template: ChatTemplateFunc = None,
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            device_map: str = "auto",
            quantization: Optional[str] = None,
            bnb_4bit_quant_type: str = "nf4",
            bnb_4bit_use_double_quant: bool = True
    ) -> None:
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

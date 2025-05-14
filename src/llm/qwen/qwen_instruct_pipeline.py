from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.llm import ModelPipeline
from src.llm import DEFAULT_SYSTEM_PROMPT


class QwenInstructPipeline(ModelPipeline):
    def __init__(self, model_name=None, device_map="auto"):
        """Class for Qwen2.5 instruct usage. For inference using huggingface transformers pipeline"""
        if model_name is None:
            model_name = "RefalMachine/ruadapt_qwen2.5_7B_ext_u48_instruct"

        super().__init__(model_name, device_map)

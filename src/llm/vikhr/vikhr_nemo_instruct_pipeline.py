from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.llm import DEFAULT_SYSTEM_PROMPT
from src.llm.model_pipeline import ModelPipeline


class VikhrNemoInstructPipeline(ModelPipeline):
    """Class for Vikhr-Nemo instruct usage. For inference using huggingface transformers pipeline"""

    def __init__(self, model_name=None, device_map="auto"):
        if model_name is None:
            model_name = "Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24"

        super().__init__(model_name, device_map)

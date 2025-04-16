from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.LLM import DEFAULT_SYSTEM_PROMPT
from src.LLM.Model_pipeline import Model_pipeline


class Vikhr_Nemo_instruct_pipeline(Model_pipeline):
    """Class for Vikhr-Nemo instruct usage. For inference using huggingface transformers pipeline"""

    def __init__(self, model_name=None, device_map="auto"):
        if model_name is None:
            model_name = "Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24"

        super().__init__(model_name, device_map)

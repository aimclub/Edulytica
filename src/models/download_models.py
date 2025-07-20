import sys
from src.llm.qwen.qwen_instruct_pipeline import QwenInstructPipeline
from src.llm.vikhr.vikhr_nemo_instruct_pipeline import VikhrNemoInstructPipeline


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Model type not provided. Usage: python download_models.py <model_type>")
        sys.exit(1)

    model_type = sys.argv[1]
    print(f"--- Downloading model for type: {model_type} ---")

    if model_type == 'qwen':
        QwenInstructPipeline()
    elif model_type == 'vikhr':
        VikhrNemoInstructPipeline()
    else:
        print(f"ERROR: Unknown model type: {model_type}")
        sys.exit(1)

    print(f"--- Model for {model_type} downloaded successfully ---")

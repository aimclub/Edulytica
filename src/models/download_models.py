import sys

from src.llm.qwen import QwenInstruct
from src.llm.vikhr import VikhrNemoInstruct

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Model type not provided. Usage: python download_models.py <model_type>")
        sys.exit(1)

    model_type = sys.argv[1]
    print(f"--- Downloading model for type: {model_type} ---")

    if model_type == 'qwen':
        QwenInstruct(quantization='8bit')
    elif model_type == 'vikhr':
        VikhrNemoInstruct(quantization='8bit')
    else:
        print(f"ERROR: Unknown model type: {model_type}")
        sys.exit(1)

    print(f"--- Model for {model_type} downloaded successfully ---")

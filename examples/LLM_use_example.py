from src.LLM.qwen.Qwen2_5_instruct import Qwen2_5_instruct

if __name__ == "__main__":
    model = Qwen2_5_instruct(quantization="8bit")
    print(model.device)
    print(model(["Привет!"]))
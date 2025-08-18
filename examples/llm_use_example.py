from edulytica.llm.qwen.QwenInstruct import QwenInstruct

if __name__ == "__main__":
    model = QwenInstruct(quantization="8bit")
    print(model.device)
    print(model(["Привет!"]))

class QuantizationException(Exception):
    def __init__(self, message=None):
        if message is None:
            message = "Unexpected quantization method. Please use 8bit or 4bit"
        super().__init__(message)

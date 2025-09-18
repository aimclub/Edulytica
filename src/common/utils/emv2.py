import re


def emv2(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+-=|{}.!])', r'\\\1', text)

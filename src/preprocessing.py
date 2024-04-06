from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from typing import List


def preprocess_text(text):
    # Удаление лишних пробелов и системных символов
    text = re.sub(r'\s+', ' ', text.strip())

    # Удаление номеров страниц (если они простые)
    text = re.sub(r'\s+\d+\s+', ' ', text)

    # Исправление гипенов и объединение разорванных слов
    text = re.sub(r'(\w+)-\s+(\w+)', lambda match: f"{match.group(1)}{match.group(2)}", text)

    # Удаление табличных данных, если они распознаются как простые строки
    # Удаление примеров со скобками, могут встречаться вокруг данных таблиц
    text = re.sub(r'\[\s*\w+\s*\|\s*\w+\s*\]', ' ', text)

    return text


def text_to_chunks(
        text: str, chunk_size: int = 500, chunk_overlap: int = 10
) -> List[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=None,
        keep_separator=True,
        is_separator_regex=False,
    )

    raw_chunks = text_splitter.create_documents([text])

    pattern = re.compile(r"'([^']+)")

    chunks = []

    for chunk in raw_chunks:
        match = pattern.search(str(chunk))
        if match:
            chunks.append(match.group(1))
        else:
            chunks.append("")

    return chunks


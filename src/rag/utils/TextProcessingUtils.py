from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from typing import List


class TextProcessingUtils:
    @staticmethod
    def preprocess_text(text):
        """
        Cleans the raw text by removing extra whitespaces, page numbers, hyphenated line-breaks,
        and table-like data if recognized as plain strings.

        :param text: The raw text to be cleaned.
        :return: The preprocessed text.
        """

        # Remove extra whitespaces and system characters
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove page numbers (if they are simple)
        text = re.sub(r'\s+\d+\s+', ' ', text)

        # Fix hyphens and join broken words
        text = re.sub(r'(\w+)-\s+(\w+)', lambda match: f"{match.group(1)}{match.group(2)}", text)

        # Remove table-like data
        text = re.sub(r'\[\s*\w+\s*\|\s*\w+\s*\]', ' ', text)

        # Remove extra spaces again after removing table-like data
        text = re.sub(r'\s+', ' ', text.strip())

        return text

    @staticmethod
    def text_to_chunks(
            text: str, chunk_size: int = 512, chunk_overlap: int = 256
    ) -> List[str]:
        """
        Splits text into chunks of a specified size with an overlap.
        Useful for breaking down text for machine learning processing.

        :param text: The text to be chunked.
        :param chunk_size: The size of each chunk (default is 512).
        :param chunk_overlap: The number of characters that adjacent chunks will overlap (default is 256).
        :return: A list of chunked text strings.
        """

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


import re
from typing import List, Tuple
from loguru import logger


class TextProcessor:
    """
    Class for processing article text and preparing it for embedding-based search
    """

    def __init__(self):
        """
        Initialize the text processor
        """
        pass

    def extract_title(self, text: str) -> str:
        """
        Extracts the article title as the first non-empty line
        :param text: Article text

        :return: Article title
        """
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return ""

    def extract_literature_section(self, text: str) -> Tuple[str, str]:
        """
        Divides the text into main part and 'Literature' (or 'References') section
        :param text: Article text

        :return: Tuple (main_text, literature_section)
        """
        pattern = re.compile(r'(^|\n)(литература|references)\s*[:\-]?\s*', re.IGNORECASE)
        match = pattern.search(text)
        if not match:
            return text.strip(), ""
        main = text[: match.start()].strip()
        literature = text[match.end():].strip()
        return main, literature

    def preprocess_article(self, text: str) -> List[str]:
        """
        Preprocesses the article and splits it into parts for further analysis
        :param text: Full article text

        :return: List of article parts for processing (title, main text, literature)
        """
        # 1. Extract title
        title = self.extract_title(text)

        # 2. Separate literature from main text
        main_with_title, literature = self.extract_literature_section(text)

        # 3. Remove title from the beginning of main text if it repeats there
        if main_with_title.startswith(title):
            main_text = main_with_title[len(title):].strip()
        else:
            main_text = main_with_title  # pragma: no cover

        # Return list of article parts
        chunks = [title, main_text, literature]

        logger.info(f"Preprocessed article into {len(chunks)} parts")
        return chunks

import unittest
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.text_processor.text_processor import TextProcessor


class TestTextProcessor(unittest.TestCase):
    """Tests for TextProcessor class"""

    def setUp(self):
        """Set up the test environment"""
        self.text_processor = TextProcessor()

    def test_extract_title(self):
        """Test extracting title from text"""
        # Text with title on the first line
        text = "Machine Learning Methods Analysis\nThis article examines...\nResearch methods"
        title = self.text_processor.extract_title(text)
        self.assertEqual(title, "Machine Learning Methods Analysis")

        # Text with empty lines before the title
        text = "\n\n  \nArticle Title\nArticle content"
        title = self.text_processor.extract_title(text)
        self.assertEqual(title, "Article Title")

        # Empty text
        text = ""
        title = self.text_processor.extract_title(text)
        self.assertEqual(title, "")

    def test_extract_literature_section(self):
        """Test splitting text into main part and literature section"""
        # Text with 'Literature' section
        text = "Introduction\nMain text\n\nЛитература:\n1. Author A. Book title. - 2020."
        main, literature = self.text_processor.extract_literature_section(text)
        self.assertEqual(main, "Introduction\nMain text")
        self.assertEqual(literature, "1. Author A. Book title. - 2020.")

        # Text with 'References' section
        text = "Main text\nSome content\n\nReferences\n1. Author A. Book title. - 2020."
        main, literature = self.text_processor.extract_literature_section(text)
        self.assertEqual(main, "Main text\nSome content")
        self.assertEqual(literature, "1. Author A. Book title. - 2020.")

        # Text without literature section
        text = "Only main text without literature"
        main, literature = self.text_processor.extract_literature_section(text)
        self.assertEqual(main, text)
        self.assertEqual(literature, "")

    def test_preprocess_article(self):
        """Test article preprocessing and splitting into parts"""
        # Complete article with title and literature
        text = "Algorithm Research\n\nIntroduction to the topic.\nLiterature review.\n\nReferences:\n1. Source 1\n2. Source 2"
        chunks = self.text_processor.preprocess_article(text)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "Algorithm Research")
        self.assertEqual(chunks[1], "Introduction to the topic.\nLiterature review.")
        self.assertEqual(chunks[2], "1. Source 1\n2. Source 2")


if __name__ == '__main__':
    unittest.main()

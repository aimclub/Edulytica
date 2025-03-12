import unittest

from Edulytica.src.rag.utils.TextProcessingUtils import TextProcessingUtils


class TestTextProcessingUtils(unittest.TestCase):

    def test_preprocess_text_removes_extra_whitespaces(self):
        raw_text = "This   is  a   test."
        expected_text = "This is a test."
        result = TextProcessingUtils.preprocess_text(raw_text)
        self.assertEqual(result, expected_text)

    def test_preprocess_text_removes_page_numbers(self):
        raw_text = "This is 1 a test 2 text."
        expected_text = "This is a test text."
        result = TextProcessingUtils.preprocess_text(raw_text)
        self.assertEqual(result, expected_text)

    def test_preprocess_text_removes_hyphenated_line_breaks(self):
        raw_text = "This is a hyphen-\nated text."
        expected_text = "This is a hyphenated text."
        result = TextProcessingUtils.preprocess_text(raw_text)
        self.assertEqual(result, expected_text)

    def test_preprocess_text_removes_table_like_data(self):
        raw_text = "This is a table [ row | column ] data."
        expected_text = "This is a table data."
        result = TextProcessingUtils.preprocess_text(raw_text)
        self.assertEqual(result, expected_text)

    def test_text_to_chunks_splits_text_correctly(self):
        text = "This is a sample text. " * 10
        chunk_size = 50
        chunk_overlap = 10
        chunks = TextProcessingUtils.text_to_chunks(text, chunk_size, chunk_overlap)

        self.assertGreater(len(chunks), 0)

        for chunk in chunks:
            self.assertLessEqual(len(chunk), chunk_size)

        self.assertIn("This is a sample text.", " ".join(chunks))

    def test_text_to_chunks_raises_value_error_for_invalid_chunk_size(self):
        text = "This is a test text."
        with self.assertRaises(ValueError):
            TextProcessingUtils.text_to_chunks(text, chunk_size=0)

    def test_text_to_chunks_raises_value_error_for_negative_chunk_overlap(self):
        text = "This is a test text."
        with self.assertRaises(ValueError):
            TextProcessingUtils.text_to_chunks(text, chunk_size=512, chunk_overlap=-1)


if __name__ == "__main__":
    unittest.main()

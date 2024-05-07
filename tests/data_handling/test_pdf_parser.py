import os.path
import unittest
from src.data_handling.pdf_parser import PDFParser


class PDFParserTest(unittest.TestCase):
    def setUp(self):
        self.test_persons_file = 'test.pdf'
        self.pdf_parser = PDFParser()

    def test_parse_file(self):
        with self.assertRaises(FileNotFoundError):
            PDFParser().parse_file('filenotexists.pdf')
        self.assertIsInstance(self.pdf_parser.parse_file(self.test_persons_file), str)

    def test_parser_files(self):
        with self.assertRaises(UnboundLocalError):
            PDFParser().parse_files('directorynotexists')
        self.assertFalse(os.path.exists('testresult.csv'))
        self.assertIsNone(self.pdf_parser.parse_files('.', 'testresult.csv'))
        self.assertTrue(os.path.exists('testresult.csv'))

    def tearDown(self):
        if os.path.exists('testresult.csv'):
            os.remove('testresult.csv')

import os.path
import unittest
from src.data_handling.pdf_parser import PDFParser


class PDFParserTest(unittest.TestCase):
    def setUp(self):
        self.tests_folder = './test/data_handling/'
        self.test_persons_file = f'{self.tests_folder}test.pdf'
        self.pdf_parser = PDFParser()

    def test_parse_file(self):
        with self.assertRaises(FileNotFoundError):
            PDFParser().parse_file(f'{self.tests_folder}filenotexists.pdf')
        self.assertIsInstance(self.pdf_parser.parse_file(self.test_persons_file), str)

    def test_parser_files(self):
        with self.assertRaises(UnboundLocalError):
            PDFParser().parse_files(f'{self.tests_folder}directorynotexists')
        self.assertFalse(os.path.exists(f'{self.tests_folder}testresult.csv'))
        self.assertIsNone(self.pdf_parser.parse_files(f'{self.tests_folder}', f'{self.tests_folder}testresult.csv'))
        self.assertTrue(os.path.exists(f'{self.tests_folder}testresult.csv'))

    def tearDown(self):
        if os.path.exists(f'{self.tests_folder}testresult.csv'):
            os.remove(f'{self.tests_folder}testresult.csv')

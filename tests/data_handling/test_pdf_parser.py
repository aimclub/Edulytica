import unittest
import os

from Edulytica.src.data_handling.pdf_parser import PDFParser


class PDFParserTest(unittest.TestCase):
    def setUp(self):
        self.tests_folder = os.path.abspath('./tests/data_handling/') + '/'
        self.test_dir = 'test_dir/'
        self.test_persons_file = f'{self.tests_folder}{self.test_dir}test.pdf'
        self.pdf_parser = PDFParser()

    def test_parse_file(self):
        with self.assertRaises(FileNotFoundError):
            self.pdf_parser.parse_file(f'{self.tests_folder}{self.test_dir}filenotexists.pdf')
        self.assertIsInstance(self.pdf_parser.parse_file(self.test_persons_file), str)

    def test_parser_files(self):
        with self.assertRaises(FileNotFoundError):
            self.pdf_parser.parse_files(f'{self.tests_folder}directorynotexists', 'testresult_noexists.csv')
        self.assertFalse(os.path.exists(f'{self.tests_folder}testresult.csv'))
        self.assertIsNone(self.pdf_parser.parse_files(f'{self.tests_folder}', 'testresult.csv'))
        self.assertTrue(os.path.exists(f'testresult.csv'))

    def tearDown(self):
        if os.path.exists(f'testresult.csv'):
            os.remove(f'testresult.csv')
        if os.path.exists(f'testresult_noexists.csv'):
            os.remove(f'testresult_noexists.csv')


if __name__ == '__main__':
    unittest.main()

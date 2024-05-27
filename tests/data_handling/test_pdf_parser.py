import unittest
import os


class PDFParserTest(unittest.TestCase):
    def setUp(self):
        from src.data_handling.pdf_parser import PDFParser
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
            self.pdf_parser.parse_files(f'{self.tests_folder}directorynotexists')
        self.assertFalse(os.path.exists(f'{self.tests_folder}testresult.csv'))
        self.assertIsNone(self.pdf_parser.parse_files(f'{self.tests_folder}', 'testresult.csv'))
        print(os.listdir(f'{self.tests_folder}'))
        self.assertTrue(os.path.exists(f'{self.tests_folder}testresult.csv'))

    def tearDown(self):
        if os.path.exists(f'{self.tests_folder}testresult.csv'):
            print('deleted')
            os.remove(f'{self.tests_folder}testresult.csv')


if __name__ == '__main__':
    unittest.main()

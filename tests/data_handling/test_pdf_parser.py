import os
import unittest

from edulytica.data_handling.PDFParser import PDFParser


class PDFParserTest(unittest.TestCase):
    def setUp(self):
        self.tests_folder = os.path.join(os.path.dirname(__file__), 'test_dir')
        self.test_persons_file = os.path.join(self.tests_folder, 'test.pdf')
        self.pdf_parser = PDFParser()

    def test_parse_file(self):
        with self.assertRaises(FileNotFoundError):
            self.pdf_parser.parse_file(os.path.join(self.tests_folder, 'filenotexists.pdf'))
        self.assertIsInstance(self.pdf_parser.parse_file(self.test_persons_file), str)

    def test_parser_files(self):
        with self.assertRaises(FileNotFoundError):
            self.pdf_parser.parse_files(
                os.path.join(self.tests_folder, 'directorynotexists'),
                'testresult_noexists.csv')
        self.assertFalse(os.path.exists(os.path.join(self.tests_folder, 'testresult.csv')))
        self.assertIsNone(self.pdf_parser.parse_files(self.tests_folder, 'testresult.csv'))
        self.assertTrue(os.path.exists('testresult.csv'))

    def tearDown(self):
        if os.path.exists('testresult.csv'):
            os.remove('testresult.csv')
        if os.path.exists('testresult_noexists.csv'):
            os.remove('testresult_noexists.csv')


if __name__ == '__main__':
    unittest.main()

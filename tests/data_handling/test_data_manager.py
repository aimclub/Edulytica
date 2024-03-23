import unittest
from src.data_handling.data_manager import DataManager


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.data_manager = DataManager(persons_json_filename='../../src/data_handling/persons.json')
        self.empty_data_manager = DataManager(persons_json_filename='../../src/data_handling/persons.json')
        self.empty_data_manager.persons_json = {}

    def test_get_processed_persons(self):
        without_empty = self.data_manager.get_processed_persons(with_empty=False, save_file_flag=False)
        with_empty = self.data_manager.get_processed_persons(with_empty=True, save_file_flag=False)
        self.assertLessEqual(without_empty.keys(), with_empty.keys())
        self.assertIsInstance(with_empty, dict)
        self.assertIsInstance(without_empty, dict)
        self.assertFalse(self.empty_data_manager.get_processed_persons(with_empty=True, save_file_flag=False))
        self.assertFalse(self.empty_data_manager.get_processed_persons(with_empty=False, save_file_flag=False))
        with self.assertRaises(FileNotFoundError):
            DataManager('filenotexists.json')

    def test_cleanse_text(self):
        self.assertEqual(self.data_manager._cleanse_text('qwe123DW'), 'qwe dw')
        self.assertEqual(self.data_manager._cleanse_text('qwe123DW', True), 'qwe123dw')
        self.assertEqual(self.data_manager._cleanse_text(''), '')
        self.assertEqual(self.data_manager._cleanse_text('1231231231231231231231'), '')
        self.assertEqual(self.data_manager._cleanse_text('ABRA ;:"*()'), 'abra')
        self.assertEqual(self.data_manager._cleanse_text('alol \n'), 'alol')
        with self.assertRaises(AttributeError):
            self.data_manager._cleanse_text(['qweqwe'])
            self.data_manager._cleanse_text([123])

    def test_factorize_persons(self):
        self.data_manager.factorization_size = 2
        self.assertEqual(self.data_manager._factorize_persons(['aaa', 'bbb', 'ccc']), [['aaa', 'bbb'], ['ccc']])
        self.data_manager.factorization_size = 1
        self.assertEqual(self.data_manager._factorize_persons(['aaa', 'bbb', 'ccc']), [['aaa'], ['bbb'], ['ccc']])
        self.data_manager.factorization_size = 1000
        self.assertEqual(self.data_manager._factorize_persons(['aaa', 'bbb', 'ccc']), [['aaa', 'bbb', 'ccc']])


if __name__ == '__main__':
    unittest.main()

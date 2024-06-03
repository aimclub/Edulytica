import unittest

from Edulytica.src.algorithms.TextComparator import TextComparator


class TestTextComparator(unittest.TestCase):

    def test_create_object(self):
        text_comparator = TextComparator
        self.assertIsNotNone(text_comparator)

    def test_correct_input_types(self):
        text_comparator = TextComparator
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 1, 1)
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 1, 'hello')
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 'hello', 1)
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 1.0001, 1.0001)
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 1.0001, 'hello')
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 'hello', 1.0001)
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, True, 'hello')
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 'hello', True)
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, [1, 1], 'hello')
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, 'hello', [1, 1])
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, [1], ['hello'])
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, ['hello'], [1])
        self.assertRaises(TypeError, text_comparator.count_percent_of_transformed_words, ['hello'], ['hello'])

    def test_correct_answers(self):
        text_comparator = TextComparator
        self.assertEqual(text_comparator.count_percent_of_transformed_words(
            'Yesterday I walked my dog for half an hour.',
            'Thoughts are all charged in favor of the project.'),
        100.00)
        self.assertEqual(text_comparator.count_percent_of_transformed_words(
            'This guy just walks there.',
            'I wanna have this ice cream.'),
            81.82)
        self.assertEqual(text_comparator.count_percent_of_transformed_words(
            'This man is simply beaming with happiness!',
            'This man is just unbearably happy about it!'),
            60.00)
        self.assertEqual(text_comparator.count_percent_of_transformed_words(
            'Yesterday I went to the store and bought a new PS4 game there!',
            'Yesterday I went to the store and bought delicious ice cream there!'),
            28.00)
        self.assertEqual(text_comparator.count_percent_of_transformed_words(
            'Yesterday I went to the store and bought a new PS4 game there!',
            'Yesterday I went to the store and bought a new PS4 game there!'),
            00.00)


if __name__ == '__main__':
    unittest.main()
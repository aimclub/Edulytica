# importing standard libraries
import string

# importing external libraries
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

# getting stopwords
stop_words = stopwords.words('russian')
# getting punctuation marks
punctuation_marks = string.punctuation


# a class for working with texts
class TextComparator:

    @staticmethod
    def count_percent_of_transformed_words(input_text_before_changing, input_text_after_changing):
        global stop_words, punctuation_marks

        if not isinstance(
                input_text_before_changing,
                str) or not isinstance(
                input_text_after_changing,
                str):
            raise TypeError("Input must be a strings")

        # getting all the words of the text
        tokens = []
        for sentence in input_text_before_changing, input_text_after_changing:
            split_text = sentence.lower().split()
            words_of_text = []
            for part_of_text in split_text:
                if part_of_text not in stop_words:
                    part_of_text_without_punctuation_marks = ''
                    for p in part_of_text:
                        if p not in punctuation_marks:
                            part_of_text_without_punctuation_marks += p
                    words_of_text.append(part_of_text_without_punctuation_marks)
            tokens.append(words_of_text)

        words_of_text_before_changing = tokens[0]
        words_of_text_after_changing = tokens[1]

        # criterion 1: number of added words
        count_of_added_words = 0
        for word in words_of_text_after_changing:
            if word not in words_of_text_before_changing:
                count_of_added_words += 1

        # criterion 2: number of deleted words
        count_of_deleted_words = 0
        for word in words_of_text_before_changing:
            if word not in words_of_text_after_changing:
                count_of_deleted_words += 1

        return round(((count_of_added_words + count_of_deleted_words) / (
            len(words_of_text_after_changing) + len(words_of_text_before_changing))) * 100, 2)

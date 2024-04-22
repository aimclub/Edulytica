import json
from string import ascii_lowercase, digits

from pymystem3.mystem import Mystem


class DataManager:
    """Class for performing string clearing operations such as removing punctuation, lemmatization, etc."""

    cyrillic_lower_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

    def __init__(self, persons_json_filename: str = 'persons.json',
                 result_json_filename: str = 'persons_result.json',
                 stop_words_filename: str = 'stop_words.txt') -> None:
        """
        :param persons_json_filename: filepath to persons.json file
        :param result_json_filename: filepath to cleansed result persons json file
        """

        self.origin_persons_filename = persons_json_filename
        self.result_persons_filename = result_json_filename
        self.stop_words_filename = stop_words_filename
        self.encoding = 'utf-8'
        with open(self.origin_persons_filename, 'r', encoding=self.encoding) as persons_file:
            self.persons_json: dict = json.load(persons_file)
        self.factorization_size = 1000

    def get_processed_persons(self, with_empty: bool = False, save_file_flag: bool = True) -> dict:
        """
        Main method for getting cleaned persons data

        :param with_empty: whether to save persons with empty fields
        :param save_file_flag: whether to save persons data
        :return: dictionary with cleaned persons data -> person's isu id is a key, cleaned string is a value
        """

        used = set()
        persons = {}
        for person_isu in self.persons_json:
            person_json = self.persons_json[person_isu]['data']

            bio, education = self._get_person_bio(person_json)
            publications = self._get_person_publications(person_json)
            projects = self._get_person_projects(person_json)
            events = self._get_person_events(person_json)

            person = ' '.join((bio, education, events, publications, projects, events)).strip()

            if with_empty or person:
                if person not in used:
                    persons[person_isu] = person
                    used.add(person)
        persons = self._lemmatize_persons(persons)
        if save_file_flag:
            self._save_persons(persons)

        return persons

    def _get_person_bio(self, person_json: dict) -> tuple[str, str]:
        """
        Method that gets the persons' cleaned bio and education data

        :param person_json: persons' data
        :return: cleaned bio and education persons' data
        """

        bio = education = ''
        if 'bio' in person_json:
            for activity in (person_json['bio']['jobs'] or []) + (person_json['bio']['duties'] or []):
                bio = f"{bio} {activity['position']['name']} {activity['department']['name']}"
            bio = self._cleanse_text(bio)

            education_json = person_json['bio']['education']
            if education_json:
                education = self._cleanse_text(education_json['faculty']['name'])
                education = self._cleanse_text(
                    f"{education} {education_json['program']['name'] if education_json['study'] == 'std' else ''}",
                    True)

        return bio, education

    def _get_person_publications(self, person_json: dict) -> str:
        """
        Method that gets the persons' cleaned publications and rids data

        :param person_json: persons' data
        :return: cleaned publications and rids persons' data
        """

        publications = ''
        for publication in (person_json['publications'] or []) + (person_json['rids'] or []):
            publications = self._cleanse_text(f"{publication['type']} {(publication['title'])}")
            publications = self._cleanse_text(f"{publications}", True)

        return publications

    def _get_person_projects(self, person_json: dict) -> str:
        """
        Method that gets the persons' cleaned projects data

        :param person_json: persons' data
        :return: cleaned projects persons' data
        """

        projects = ''
        for project in person_json['projects'] or []:
            projects = self._cleanse_text(f"{project['type']} {project['title']} {' '.join(project['key_words'])} "
                                          f"{project['role']} {project['customer']}")

        return projects

    def _get_person_events(self, person_json: dict) -> str:
        """
        Method that gets the persons' cleaned events data

        :param person_json: persons' data
        :return: cleaned events persons' data
        """

        events = ''
        for event in person_json['events'] or []:
            events = self._cleanse_text(f"{event['rank']} "
                                        f"{event['title']} {event['type']} {event['role']}")
            events = self._cleanse_text(f"{events}", True)

        return events

    def _cleanse_text(self, text: str, allow_digits: bool = False) -> str:
        """
        Method that clears text to remove non-alphabetic characters

        :param text: original text
        :param allow_digits: whether to save digits in the text or not
        :return: result text without special characters
        """

        for let in set(text):
            if let.lower() not in ascii_lowercase + self.cyrillic_lower_letters + ' ' + digits * allow_digits:
                text = text.replace(let, ' ')
        text = self.remove_stop_words(text.lower())
        return text

    def _lemmatize_persons(self, original_persons: dict) -> dict:
        """
        Method that lemmatizes persons' data.
        for faster lemmatization, it combines persons to groups and run algorithm together.
        You can change the size class parameter to reshape the groups

        :param original_persons: original persons dictionary
        :return: lemmatized persons dictionary
        """

        persons_isu_ids, persons_texts = list(original_persons.keys()), list(original_persons.values())
        factorized_persons = self._factorize_persons(persons_texts)
        result = []
        mystem = Mystem()
        for part in factorized_persons:
            all_texts = ' '.join([f'{txt} br ' for txt in part])
            words = mystem.lemmatize(all_texts)
            doc = []
            for txt in words:
                if txt != '\n' and txt.strip():
                    if txt == 'br':
                        result.append(self._cleanse_text(' '.join(doc), allow_digits=True))
                        doc = []
                    else:
                        doc.append(txt)
        persons = dict(zip(persons_isu_ids, result))
        return persons

    def _factorize_persons(self, persons: list[str]) -> list[list[str]]:
        """
        Method for decomposing the persons list into several lists of strings of the size parameter

        :param persons: original list of persons
        :return: list of strings containing persons' data
        """

        return [persons[i:i + self.factorization_size] for i in range(0, len(persons), self.factorization_size)]

    def _save_persons(self, persons: dict, filepath: str = None) -> None:
        """
        Method for saving the persons dictionary

        :param persons: persons dictionary, key is person's isu id, value is person's data
        :param filepath: filepath where to save the persons dictionary
        :return:
        """
        json.dump(persons, open(filepath or self.result_persons_filename, 'w', encoding=self.encoding),
                  ensure_ascii=False, indent=2)

    def remove_stop_words(self, text: str) -> str:
        """
        Method for removing stop words from text

        :param text: original string
        :return: text without stop words
        """
        stop_words = set(open(self.stop_words_filename, 'r', encoding=self.encoding).readline().split())
        return ' '.join(word for word in text.split() if word not in stop_words)


if __name__ == '__main__':
    dw = DataManager()
    print(dw.get_processed_persons())

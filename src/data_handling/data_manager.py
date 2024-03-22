import json
from string import ascii_lowercase, digits


class DataManager:
    cyrillic_lower_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

    def __init__(self, persons_json_filename='persons.json'):
        self.persons_json: dict = json.load(open(persons_json_filename, 'r', encoding='utf-8'))

    def get_processed_persons(self) -> dict:
        persons = {}
        for person_isu in self.persons_json:
            person_json = self.persons_json[person_isu]['data']

            bio, education = self._get_person_bio(person_json)
            publications = self._get_person_publications(person_json)
            projects = self._get_person_projects(person_json)
            events = self._get_person_events(person_json)

            person = {'bio': bio, 'education': education, 'events': ' '.join((publications, projects, events)).strip()}
            persons[person_isu] = person

        return persons

    def _get_person_bio(self, person_json: dict) -> tuple[str, str]:
        bio = education = ''
        if 'bio' in person_json:
            for activity in (person_json['bio']['jobs'] or []) + (person_json['bio']['duties'] or []):
                bio = f"{bio} {activity['position']['name']} {activity['department']['name']}"
            bio = self._cleanse_text(bio)

            education_json = person_json['bio']['education']
            if education_json:
                education = self._cleanse_text(education_json['faculty']['name'])
                education = self._cleanse_text(
                    f"{education} {education_json['year']}"
                    f" {education_json['program']['name'] if education_json['study'] == 'std' else ''}", True)

        return bio, education

    def _get_person_publications(self, person_json: dict) -> str:
        publications = ''
        for publication in (person_json['publications'] or []) + (person_json['rids'] or []):
            publications = self._cleanse_text(f"{publication['type']} {(publication['title'])}")
            publications = self._cleanse_text(f"{publications} {publication['year']}", True)

        return publications

    def _get_person_projects(self, person_json: dict) -> str:
        projects = ''
        for project in person_json['projects'] or []:
            projects = self._cleanse_text(f"{project['type']} {project['title']} {' '.join(project['key_words'])} "
                                          f"{project['role']} {project['customer']}")

        return projects

    def _get_person_events(self, person_json: dict) -> str:
        events = ''
        for event in person_json['events'] or []:
            events = self._cleanse_text(f"{event['rank']} "
                                        f"{event['title']} {event['type']} {event['role']}")
            events = self._cleanse_text(f"{events} {event['year']}", True)

        return events

    def _cleanse_text(self, text: str, allow_digits: bool = False) -> str:
        for let in set(text):
            if let.lower() not in ascii_lowercase + self.cyrillic_lower_letters + ' ' + digits * allow_digits:
                text = text.replace(let, '')
        text = ' '.join(word for word in text.lower().split())
        return text

    @staticmethod
    def _factorize_persons(persons: list, size: int = 1000) -> list[list[tuple[str, dict]]]:
        return [persons[i:i + size] for i in range(0, len(persons), size)]


if __name__ == '__main__':
    dw = DataManager()
    print(dw.get_processed_persons())

import json
from random import random
from dotenv import load_dotenv
import os
import requests
from time import sleep
from bs4 import BeautifulSoup as BSoup

load_dotenv('./isu-env')


class ParserISU:
    """
    This class is responsible for parsing ISU persons' data: education, publications, rids, projects and events
    """

    def __init__(self, cookie: str, remember_sso: str) -> None:
        """
        :param cookie: ISU user's cookie token
        :param remember_sso: ISU user's remember_sso token
        """
        self.cookies = {'ISU_AP_COOKIE': cookie,
                        'REMEMBER_SSO': remember_sso}

    def parse_users_data(self) -> None:
        """
        main method to parse persons data from ISU website
        writes parsed data to json file -> persons.json
        :return:
        """
        base_isu_person_link = 'https://isu.itmo.ru/person/'
        try:
            # Copying parsed data for backup
            json.dump(json.load(open('persons.json', 'r', encoding='utf-8')),
                      open('persons_copy.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

            persons = json.load(open('persons.json', 'r', encoding='utf-8'))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            persons = {}

        # isu ids that don't relate to any person
        try:
            no_exist_isu_ids = open('no_exist_isu_ids.txt', 'r', encoding='utf-8').read().split()
        except FileNotFoundError:
            no_exist_isu_ids = []

        try:
            reserve_saving_counter = 0
            for isu_person_id in range(287434, int(1e6)):
                person_link = base_isu_person_link + str(isu_person_id)
                print(f'user {isu_person_id} started -> {person_link}', end=' ')

                try:
                    response = requests.get(person_link, cookies=self.cookies, timeout=1.5)
                    open('page.html', 'w', encoding='utf-8').write(response.text)
                except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                    no_exist_isu_ids.append(isu_person_id)
                    print(f'does not exist {reserve_saving_counter}/100 to reserve save')
                else:
                    persons[str(isu_person_id)] = {'isu_id': str(isu_person_id),
                                                   'data': self.parse_data_from_html(response.text)}
                    reserve_saving_counter += 1
                    print(f'done {reserve_saving_counter}/100 to reserve save')

                if reserve_saving_counter >= 100:
                    reserve_saving_counter = 0
                    open('persons.json', 'w', encoding='utf-8').write(json.dumps(persons, indent=2, ensure_ascii=False))
                    open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(' '.join(map(str, no_exist_isu_ids)))
                    print('saved')
                sleep(1 + random())
        except KeyboardInterrupt:
            return
        finally:
            open('persons.json', 'w', encoding='utf-8').write(json.dumps(persons, indent=2, ensure_ascii=False))
            open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(' '.join(map(str, no_exist_isu_ids)))

    def parse_data_from_html(self, html_text: str) -> dict:
        """
        requires person's html page text and return dictionary with data from html page which contains users information

        :param html_text: person's page in string format
        :return: parsed data as dictionary with keys 'publications', 'rids', 'projects', 'events' or None if no data is found
        """
        soup = BSoup(html_text, 'html.parser')
        return {'bio': self.parse_bio(soup),
                'publications': self.parse_publications(soup),
                'rids': self.parse_rids(soup),
                'projects': self.parse_projects(soup),
                'events': self.parse_events(soup)}

    def parse_publications(self, soup: BSoup) -> list[dict] or None:
        """
        requires person's html page text and return list of dictionaries with person's publications

        :param soup: BeautifulSoup object of person's html page
        :return: person's publications list which contains
                 dictionaries with keys 'type', 'year', 'authors', 'title' or None if no data is found
        """
        try:
            data: dict = self.extract_data_from_soup(soup.find('span', id='R1724073431179133097').find('script'))
        except (TypeError, AttributeError):
            return None
        publications = []
        for row in data['data']:
            year_index = row[3].find('>') + 1
            publications.append({'type': row[1],
                                 'year': int(row[3][year_index:year_index + 4]),
                                 'authors': self.parse_authors(row[2]),
                                 'title': row[2][row[2].rfind('</a>') + 5:]})
        return publications

    def parse_rids(self, soup: BSoup) -> list[dict] or None:
        """
        requires person's html page text and return list of dictionaries with person's rids

        :param soup: BeautifulSoup object of person's html page
        :return: person's rids list which contains
                 dictionaries with keys 'year', 'type', 'title', 'authors' or None if no data is found
        """

        try:
            data: dict = self.extract_data_from_soup(soup.find('span', id='R1724086259370226350').find('script'))
        except (TypeError, AttributeError):
            return None
        rids = []
        for row in data['data']:
            year_index = row[1].find('>') + 1
            rids.append({
                'year': int(row[1][year_index:year_index + 4]),
                'type': row[2].strip(),
                'title': row[3].strip(),
                'authors': self.parse_authors(row[5])})
        return rids

    def parse_projects(self, soup: BSoup) -> list[dict] or None:
        """
        requires person's html page text and return list of dictionaries with person's projects

        :param soup: BeautifulSoup object of person's html page
        :return: person's projects list which contains dictionaries
        with keys 'theme_id', 'type', 'title', 'department_id', 'date_start', 'date_end',
        'key_words', 'role', 'customer' or None if no data is found
        """

        try:
            data: dict = self.extract_data_from_soup(soup.find('span', id='R1724464641275058427').find('script'))
        except (TypeError, AttributeError):
            return None
        projects = []
        for row in data['data']:
            projects.append({
                'theme_id': int(row[1]),
                'type': row[2].strip(),
                'title': row[3].strip(),
                'department_id': int(row[4][row[4].find('[') + 1:row[4].find(']')]),
                'date_start': row[5].strip(),
                'date_end': row[6].strip(),
                'key_words': tuple(el.strip() for el in row[7].split(',')),
                'role': row[9].strip(),
                'customer': row[10].strip()})
        return projects

    def parse_events(self, soup: BSoup) -> list[dict] or None:
        """
        requires person's html page text and return list of dictionaries with person's events

        :param soup: BeautifulSoup object of person's html page
        :return: person's events list which contains
                 dictionaries with keys 'title', 'year', 'type', 'rank', 'role' or None if no data is found
        """

        try:
            data: dict = self.extract_data_from_soup(soup.find('div', id='R1293424228395371640').find('script'))

        except (TypeError, AttributeError):
            return None
        events = []
        for row in data['data']:
            events.append({
                'title': row[0].strip(),
                'year': int(row[2]) if row[2] else '',
                'type': row[3].strip(),
                'rank': row[4].strip(),
                'role': row[5].strip()})
            if ' - ' in row[1]:
                events[-1]['date_start'] = row[1][row[1].find('>') + 1:row[1].find(' - ')].strip()
                events[-1]['date_end'] = row[1][row[1].find(' - ') + 3:row[1].rfind('<')].strip()
            else:
                events[-1]['date_start'] = events[-1]['date_end'] = row[1][
                                                                    row[1].find('>') + 1:row[1].rfind('<')].strip()
        return events

    def parse_bio(self, soup: BSoup) -> list[dict] or None:
        """
        requires person's html page text and return list of dictionaries with person's current education

        :param soup: BeautifulSoup object of person's html page
        :return: person's current education list which contains
                 dictionaries with keys  or None if no data is found
        """

        data_job, data_duties, data_education = self.extract_bio_from_soup(soup)
        person_bio = {'jobs': [], 'duties': [], 'education': {}}

        for job in data_job:
            position = job['position']
            person_bio['jobs'].append(
                {'position': {'id': position['id'], 'name': position['name'],
                              'rate': float(position['rate']['value'])},
                 'department': {'id': job['department']['id'],
                                'name': job['department']['name']}})

        for duty in data_duties:
            person_bio['duties'].append(
                {'position': {'id': duty['position']['id'], 'name': duty['position']['name']},
                 'department': duty['str']})

        if data_education is not None:
            person_bio['education'] = {'year': data_education['year'],
                                       'faculty': {'id': data_education['faculty']['id'],
                                                   'name': data_education['faculty']['name']}}
            if 'stud' in data_education:
                person_bio['education']['study'] = 'std'
                person_bio['education']['program'] = {'id': data_education['program']['id'],
                                                      'name': data_education['program']['name']}
            elif 'asp' in data_education:
                person_bio['education']['study'] = 'asp'
            else:
                print(data_education.keys())

        return person_bio

    @staticmethod
    def extract_bio_from_soup(soup: BSoup) -> tuple:
        try:
            data_job: list = json.loads(
                soup.find('span', attrs={'data-mustache-template': 'person-job'}).contents[0])['positions']
        except (TypeError, AttributeError):
            data_job = []
        try:
            data_duties: list = json.loads(
                soup.find('span', attrs={'data-mustache-template': 'person-duties'}).contents[0])['positions']
        except (TypeError, AttributeError):
            data_duties = []
        try:
            data_education: dict = json.loads(
                soup.find('span', attrs={'data-mustache-template': 'person-edu'}).contents[0])['education'][0]
        except (TypeError, AttributeError):
            data_education = None
        return data_job, data_duties, data_education

    @staticmethod
    def extract_data_from_soup(data: BSoup) -> dict:
        """
        static method to extract person's data from html string

        :param data: person's page html fragment containing data
        :return: dictionary with person's data
        """
        data = str(data)
        data: dict = json.loads(data[data.find('jsonData={') + 9:data.find('};') + 1].replace('&quot', "'"))
        data.pop('recordsFiltered')
        return data

    @staticmethod
    def parse_authors(authors_string: str) -> list:
        """
        static method to extract authors of the person's publication from html string

        :param authors_string: person's page html fragment containing publication's authors
        :return: list of person's publication authors
        """
        authors = []
        for author in authors_string.split('</a>')[:-1]:
            first_quote = author.find('"')
            second_quote = author.find('"', first_quote + 1)
            third_quote = author.find('"', second_quote + 1)
            fourth_quote = author.find('"', third_quote + 1)
            author = {'isu_profile': author[first_quote + 1:second_quote].strip(),
                      'name': author[third_quote + 1:fourth_quote].strip()}
            authors.append(author)
        return authors


if __name__ == '__main__':
    parser = ParserISU(os.getenv('ISU_COOKIE'),
                       os.getenv('SSO_REMEMBER'))

    parser.parse_users_data()

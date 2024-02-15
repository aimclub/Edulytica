import json
from random import random

import requests
from time import sleep
from bs4 import BeautifulSoup as BSoup


class ParserISU:
    def __init__(self, cookie: str, remember_sso):
        self.cookies = {'ISU_AP_COOKIE': cookie,
                        'REMEMBER_SSO': remember_sso}

    def parse_users_data(self):
        base_isu_person_link = 'https://isu.itmo.ru/person/'

        try:
            persons: dict = json.load(open('persons.json', 'r', encoding='utf-8'))
            open('persons.json', 'w', encoding='utf-8')
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            persons = {}
        try:
            no_exist_isu_ids = open('no_exist_isu_ids.txt', 'r', encoding='utf-8').read().split()
            open('no_exist_isu_ids.txt', 'w', encoding='utf-8')
        except FileNotFoundError:
            no_exist_isu_ids = []
        for isu_person_id in range(103466, int(1e6)):
            person_link = base_isu_person_link + str(isu_person_id)
            print(f'user {isu_person_id} started -> {person_link}')
            try:
                response = requests.get(person_link, cookies=self.cookies, timeout=5)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                no_exist_isu_ids.append(isu_person_id)
                open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(' '.join(map(str, no_exist_isu_ids)))
            else:
                persons[isu_person_id] = {'isu_id': isu_person_id, 'data': self.parse_data_from_html(response.text)}
            finally:
                open('persons.json', 'w', encoding='utf-8').write(json.dumps(persons, indent=2, ensure_ascii=False))
            print(f'user {isu_person_id} done')
            sleep(120 + random())

    def parse_data_from_html(self, html_text):
        soup = BSoup(html_text, 'html.parser')

        return {'publications': self.parse_publications(soup),
                'rids': self.parse_rids(soup),
                'projects': self.parse_projects(soup),
                'events': self.parse_events(soup)}

    def parse_publications(self, soup: BSoup):
        try:
            data: dict = self.extract_data_from_soup(str(soup.find('span', id='R1724073431179133097').find('script')))
        except AttributeError:
            return None
        publications = []
        for row in data['data']:
            year_index = row[3].find('>') + 1
            publications.append({'type': row[1],
                                 'year': int(row[3][year_index:year_index + 4]),
                                 'authors': self.parse_authors(row[2]),
                                 'title': row[2][row[2].rfind('</a>') + 5:]})
        return publications

    def parse_rids(self, soup: BSoup):
        try:
            data: dict = self.extract_data_from_soup(str(soup.find('span', id='R1724086259370226350').find('script')))
        except AttributeError:
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

    def parse_projects(self, soup: BSoup):
        try:
            data: dict = self.extract_data_from_soup(str(soup.find('span', id='R1724464641275058427').find('script')))
        except AttributeError:
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

    def parse_events(self, soup: BSoup):
        try:
            data: dict = self.extract_data_from_soup(str(soup.find('div', id='R1293424228395371640').find('script')))
        except AttributeError:
            return None
        events = []
        for row in data['data']:
            events.append({
                'title': row[0].strip(),
                'year': int(row[2]),
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

    @staticmethod
    def extract_data_from_soup(data: str):
        data: dict = json.loads(data[data.find('jsonData={') + 9:data.find('};') + 1])
        data.pop('recordsFiltered')
        return data

    @staticmethod
    def parse_authors(authors_string: str) -> list:
        authors = []
        for author in authors_string.split(','):
            first_quote = author.find('"')
            second_quote = first_quote + author[first_quote + 1:].find('"') + 1
            third_quote = second_quote + author[second_quote + 1:].find('"') + 1
            fourth_quote = third_quote + author[third_quote + 1:].find('"') + 1
            author = {'isu_profile': author[first_quote + 1:second_quote],
                      'name': author[third_quote + 1: fourth_quote]}
            authors.append(author)
        return authors


if __name__ == '__main__':
    parser = ParserISU('ORA_WWV-LpNjxV3XfSsXG419xIqJ9BMi',
                       '5C0DBBEF3E6209E2077AFCB2489C6CA4:188760328BF889B6C00003C2D225BEC3D5A915796C6C2E33822C27B362AA82248E2D5FF3B06EE15B9A5DE1155EF6A1B3')

    parser.parse_users_data()
    # print(parser.parse_data_from_html(open('page.html', 'r', encoding='utf-8').read()))

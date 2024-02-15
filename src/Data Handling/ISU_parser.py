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

        for isu_person_id in range(103466, int(1e6)):
            sleep(0.2 + random())
            person_link = base_isu_person_link + str(isu_person_id)
            try:
                response = requests.get(person_link, cookies=self.cookies)
                print(isu_person_id, response.status_code)
                person_data = self.parse_data_from_html(response.text)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                print(f'User with ISU id {isu_person_id} does not exist')

            open('page.html', 'w', encoding='utf-8').write(response.text)
            break

    def parse_data_from_html(self, html_text):
        soup = BSoup(html_text, 'html.parser')

        data = {'publications': self.parse_publications(soup),
                'rids': self.parse_rids(soup),
                'projects': self.parse_projects(soup),
                'events': self.parse_events(soup)}
        return data

    def parse_publications(self, soup: BSoup):
        data = self.extract_data_from_soup(soup)
        publications = []
        for row in data['data']:
            year_index = row[3].find('>') + 1
            publications.append({'type': row[1],
                                 'year': int(row[3][year_index:year_index + 4]),
                                 'authors': self.parse_authors(row[2]),
                                 'title': row[2][row[2].rfind('</a>') + 5:]})
        return publications

    def parse_rids(self, soup: BSoup):
        data = self.extract_data_from_soup(soup)
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
        data = self.extract_data_from_soup(soup)
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
        data = self.extract_data_from_soup(soup)
        events = []
        for row in data['data']:
            events.append({
                'title': row[0].strip(),
                'date_start': row[1][row[1].find('>') + 1:row[1].find(' - ')].strip(),
                'date_end': row[1][row[1].find(' - ') + 3:row[1].rfind('<')].strip(),
                'year': int(row[2]),
                'type': row[3].strip(),
                'rank': row[4].strip(),
                'role': row[5].strip()})
        return events

    @staticmethod
    def extract_data_from_soup(soup: BSoup):
        data: str = str(soup.find('div', id='R1293424228395371640').find('script'))
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
    parser = ParserISU('your_cookie',
                       'your_sso_token')

    # parser.parse_users_data()
    print(parser.parse_data_from_html(open('page.html', 'r', encoding='utf-8').read()))

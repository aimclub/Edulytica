import asyncio
import json
from random import random

import aiohttp
from aiohttp import ClientTimeout
from dotenv import load_dotenv
import os
from time import sleep
from bs4 import BeautifulSoup as BSoup

"""
before launching you need to insert your ISU_cookie and SSO_REMEMBER to isu-env file
"""
load_dotenv('./isu-env')


class ParserISU:
    """
    This class is responsible for parsing ISU persons' data: education, publications, rids, projects and events
    Use parse_users_date method to parse
    """

    def __init__(self, cookie: str, remember_sso: str) -> None:
        """
        :param cookie: ISU user's cookie token
        :param remember_sso: ISU user's remember_sso token
        """

        self.base_isu_person_link = 'https://isu.itmo.ru/person/'
        self.cookies = {'ISU_AP_COOKIE': cookie,
                        'REMEMBER_SSO': remember_sso}
        self.async_requests = []
        self.async_responses = []

    async def parse_all_isu_ids(self):
        try:
            persons = set(map(int, json.load(open('persons.json', 'r', encoding='utf-8')).keys()))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            persons = set()
        try:
            no_exist_isu_ids = set(map(int, open('no_exist_isu_ids.txt', 'r', encoding='utf-8').read().split()))
        except FileNotFoundError:
            no_exist_isu_ids = set()
        try:
            reserve_saving_number = 0
            for isu_person_id in range(300000, 10 ** 6):
                if isu_person_id in no_exist_isu_ids or isu_person_id in persons:
                    print(f'{isu_person_id} already done')
                    continue
                self.async_requests.append(isu_person_id)
                if len(self.async_requests) < 5:
                    continue
                self.async_responses.clear()
                tasks = [self._parse_website(i) for i in self.async_requests]
                self.async_requests.clear()
                await asyncio.gather(*tasks)
                for i, response in self.async_responses:
                    reserve_saving_number += 1
                    if response:
                        persons.add(i)
                        print(f'{i} found -> {reserve_saving_number}/100 to save')
                    else:
                        no_exist_isu_ids.add(i)
                        print(f'{i} does not exist -> {reserve_saving_number}/100 to save')
                    if reserve_saving_number >= 100:
                        reserve_saving_number = 0
                        open('persons_ids.txt', 'w', encoding='utf-8').write(' '.join(map(str, sorted(persons))))
                        open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(
                            ' '.join(map(str, sorted(no_exist_isu_ids))))
                        print(i, 'saved')
        except KeyboardInterrupt:
            return print('Keyboard Interrupt')
        finally:
            print(isu_person_id)
            open('persons_ids.txt', 'w', encoding='utf-8').write(' '.join(map(str, sorted(persons))))
            open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(' '.join(map(str, sorted(no_exist_isu_ids))))

    def parse_users_data(self, start_isu=0):
        asyncio.run(self._async_parse_users_data(start_isu))

    async def _async_parse_users_data(self, start_isu=0):
        try:
            # Copying parsed data for backup
            json.dump(json.load(open('persons.json', 'r', encoding='utf-8')),
                      open('persons_copy.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

            persons = json.load(open('persons.json', 'r', encoding='utf-8'))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            persons = {}

        # isu ids that don't relate to any person
        try:
            no_exist_isu_ids = set(open('no_exist_isu_ids.txt', 'r', encoding='utf-8').read().split())
        except FileNotFoundError:
            no_exist_isu_ids = set()

        try:
            reserve_saving_counter = 0
            for isu_person_id in range(start_isu, 10 ** 6):
                if str(isu_person_id) in no_exist_isu_ids or str(isu_person_id) in persons:
                    print(f'already have the person: {isu_person_id}')
                    continue
                sleep(.2 + random() * .5)
                person_link = self.base_isu_person_link + str(isu_person_id)
                print(f'user {isu_person_id} added -> {person_link}')
                self.async_requests.append(isu_person_id)

                if len(self.async_requests) < 5:
                    continue

                self.async_responses.clear()
                tasks = [self._parse_website(i) for i in self.async_requests]
                self.async_requests.clear()

                await asyncio.gather(*tasks)
                for i, response in self.async_responses:
                    reserve_saving_counter += 1
                    if response:
                        persons[i] = {'isu_id': str(i), 'data': self._parse_data_from_html(response)}
                        print(f'{i} done', end='\t|\t')
                    else:
                        no_exist_isu_ids.add(str(i))
                        print(f'{i} not exists', end='\t|\t')
                print()
                print(f'{reserve_saving_counter}/100 to reserve save')
                if reserve_saving_counter >= 100:
                    reserve_saving_counter = 0
                    open('persons.json', 'w', encoding='utf-8').write(
                        json.dumps(persons, indent=2, ensure_ascii=False))
                    open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(
                        ' '.join(map(str, sorted(map(int, no_exist_isu_ids)))))
                    print('saved')
        except KeyboardInterrupt:
            return print('Keyboard Interrupt')
        finally:
            print(isu_person_id)
            open('persons.json', 'w', encoding='utf-8').write(json.dumps(persons, indent=2, ensure_ascii=False))
            open('no_exist_isu_ids.txt', 'w', encoding='utf-8').write(
                ' '.join(map(str, sorted(map(int, no_exist_isu_ids)))))

    async def _fetch_url(self, url):
        async with aiohttp.ClientSession(cookies=self.cookies, timeout=ClientTimeout(1.5)) as session:
            async with session.get(url) as response:
                return await response.text()

    async def _parse_website(self, isu_user_id):
        try:
            self.async_responses.append(
                (isu_user_id, await self._fetch_url(f'{self.base_isu_person_link}{isu_user_id}')))
        except asyncio.exceptions.TimeoutError:
            self.async_responses.append((isu_user_id, None))

    def _parse_data_from_html(self, html_text: str) -> dict:
        """
        Requires person's html page text and return dictionary with data from html page which contains users information

        :param html_text: person's page in string format
        :return: parsed data as dictionary or None if no data is found
        """

        soup = BSoup(html_text, 'html.parser')
        return {'bio': self._parse_bio(soup),
                'publications': self._parse_publications(soup),
                'rids': self._parse_rids(soup),
                'projects': self._parse_projects(soup),
                'events': self._parse_events(soup)}

    def _parse_publications(self, soup: BSoup) -> list[dict] or None:
        """
        Requires person's html page text and return list of dictionaries with person's publications

        :param soup: BeautifulSoup object of person's html page
        :return: person's publications list which contains dictionaries or None if no data is found
        """

        try:
            data: dict = self._extract_data_from_soup(soup.find('span', id='R1724073431179133097').find('script'))
        except (TypeError, AttributeError, json.decoder.JSONDecodeError):
            return None
        publications = []
        for row in data['data']:
            year_index = row[3].find('>') + 1
            publications.append({'type': row[1],
                                 'year': int(row[3][year_index:year_index + 4]),
                                 'authors': self._parse_authors(row[2]),
                                 'title': row[2][row[2].rfind('</a>') + 5:]})
        return publications

    def _parse_rids(self, soup: BSoup) -> list[dict] or None:
        """
        Requires person's html page text and return list of dictionaries with person's rids

        :param soup: BeautifulSoup object of person's html page
        :return: person's rids list which contains dictionaries or None if no data is found
        """

        try:
            data: dict = self._extract_data_from_soup(soup.find('span', id='R1724086259370226350').find('script'))
        except (TypeError, AttributeError):
            return None
        rids = []
        for row in data['data']:
            year_index = row[1].find('>') + 1
            rids.append({
                'year': int(row[1][year_index:year_index + 4]),
                'type': row[2].strip(),
                'title': row[3].strip(),
                'authors': self._parse_authors(row[5])})
        return rids

    def _parse_projects(self, soup: BSoup) -> list[dict] or None:
        """
        Requires person's html page text and return list of dictionaries with person's projects

        :param soup: BeautifulSoup object of person's html page
        :return: person's projects list which contains dictionaries or None if no data is found
        """

        try:
            data: dict = self._extract_data_from_soup(soup.find('span', id='R1724464641275058427').find('script'))
        except (TypeError, AttributeError):
            return None
        projects = []
        for row in data['data']:
            department_id = row[4][row[4].find('[') + 1:row[4].find(']')]
            projects.append({
                'theme_id': int(row[1]),
                'type': row[2].strip(),
                'title': row[3].strip(),
                'department_id': int(row[4][row[4].find('[') + 1:row[4].find(']')] if department_id else 0),
                'date_start': row[5].strip(),
                'date_end': row[6].strip(),
                'key_words': tuple(el.strip() for el in row[7].split(',')),
                'role': row[9].strip(),
                'customer': row[10].strip()})
        return projects

    def _parse_events(self, soup: BSoup) -> list[dict] or None:
        """
        Requires person's html page text and return list of dictionaries with person's events

        :param soup: BeautifulSoup object of person's html page
        :return: person's events list which contains
                 dictionaries with keys 'title', 'year', 'type', 'rank', 'role' or None if no data is found
        """

        try:
            data: dict = self._extract_data_from_soup(soup.find('div', id='R1293424228395371640').find('script'))

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

    def _parse_bio(self, soup: BSoup) -> list[dict] or None:
        """
        Requires person's html page text and return list of dictionaries with person's current education

        :param soup: BeautifulSoup object of person's html page
        :return: person's current education list which contains
                 dictionaries with keys  or None if no data is found
        """

        data_job, data_duties, data_education = self._extract_bio_from_soup(soup)
        person_bio = {'jobs': [], 'duties': [], 'education': {}}

        for job in data_job:
            position = job['position']
            person_bio['jobs'].append(
                {'position': {'id': int(position['id']), 'name': position['name'],
                              'rate': float(position['rate']['value']) if position['rate'] is not None else 1.},
                 'department': {'id': int(job['department']['id']),
                                'name': job['department']['name']}})

        for duty in data_duties:
            person_bio['duties'].append(
                {'position': {'id': int(duty['position']['id']), 'name': duty['position']['name']},
                 'department': duty['str']})

        if data_education is not None:
            person_bio['education'] = {'year': int(data_education['year']),
                                       'faculty': {'id': int(data_education['faculty']['id']),
                                                   'name': data_education['faculty']['name']}}
            if 'stud' in data_education:
                person_bio['education']['study'] = 'std'
                person_bio['education']['program'] = {'id': int(data_education['program']['id'] or '0'),
                                                      'name': data_education['program']['name']}
            elif 'asp' in data_education:
                person_bio['education']['study'] = 'asp'
            else:
                print(data_education.keys())

        return person_bio

    @staticmethod
    def _extract_bio_from_soup(soup: BSoup) -> tuple:
        """
        Extracts bio from soup object

        :param soup: BeautifulSoup object of person bio
        :return: tuple of data_job, data_duties and data_education
        """

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
    def _extract_data_from_soup(data: BSoup) -> dict | None:
        """
        Static method to extract person's data from html string

        :param data: person's page html fragment containing data
        :return: dictionary with person's data
        """

        data = str(data)
        data: dict = json.loads(data[data.find('jsonData={') + 9:data.find('};') + 1].replace('&quot', "'"))
        data.pop('recordsFiltered')
        return data

    @staticmethod
    def _parse_authors(authors_string: str) -> list:
        """
        Static method to extract authors of the person's publication from html string

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

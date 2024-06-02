import asyncio
import json
import os
from random import random
from time import sleep

import aiohttp
import requests
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup as BSoup, Tag
from dotenv import load_dotenv

"""
before launching you need to insert your ISU_cookie and SSO_REMEMBER to isu-env file
"""
load_dotenv('./isu-env')


class ParserISU:
    """
    This class is responsible for parsing ISU persons' data: education, publications, rids, projects and events
    Use parse_users_data method to parse
    """

    def __init__(self, cookie: str, remember_sso: str) -> None:
        """
        :param cookie: ISU user's cookie token
        :param remember_sso: ISU user's remember_sso token
        """

        self.base_isu_person_link = 'https://isu.itmo.ru/person/'
        self.registration_host_url = 'id.itmo.ru'
        self.isu_id_to_check_connection = 409878

        self.persons_filename = 'persons.json'
        self.no_exists_persons_filename = 'no_exist_isu_ids.txt'
        self.persons_copy_filename = 'persons_copy.json'

        self.session_exception_message = 'Your cookie is expired or None'
        self.ip_address_exception_message = 'Your ip address is not valid. You need to use ITMO ip address or ITMO vpn'
        self.successful_connection_message = 'Connection established'
        self.requests_limit = 5  # limit on requests sent at one time
        self.requests_count_to_save = 100
        self.requests_cooldown_seconds = .2

        self.cookies = {'ISU_AP_COOKIE': cookie,
                        'REMEMBER_SSO': remember_sso}
        self.async_requests = []
        self.async_responses = []

    def parse_users_data(self, start_isu: int = 0):
        """
        Main method that runs the asynchronous parse method
        Launches async method

        :param start_isu: isu to start parsing from
        """

        asyncio.run(self._async_parse_users_data(start_isu))

    async def _async_parse_users_data(self, start_isu: int) -> None:
        """
        Method to asynchronous parse persons data from ISU website
        Writes parsed data to json file -> persons.json

        :param start_isu: isu to start parsing from
        """

        connection_troubles = self._check_connection()
        if connection_troubles:
            return print(connection_troubles)

        try:
            # Copying parsed data for backup
            json.dump(json.load(open(self.persons_filename, 'r', encoding='utf-8')),
                      open(self.persons_copy_filename, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

            persons = json.load(open(self.persons_filename, 'r', encoding='utf-8'))
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(e)
            persons = {}

        # isu ids that don't relate to any person
        try:
            no_exist_isu_ids = set(open(self.no_exists_persons_filename, 'r', encoding='utf-8').read().split())
        except FileNotFoundError:
            no_exist_isu_ids = set()

        isu_person_id = start_isu
        try:
            saving_counter = 0
            self.async_requests = []
            self.async_responses = []
            for isu_person_id in range(start_isu, 10 ** 6):
                if str(isu_person_id) in no_exist_isu_ids or str(isu_person_id) in persons:
                    print(f'already have the person: {isu_person_id}')
                    continue

                sleep(self.requests_cooldown_seconds + random() * .5)

                print(f'user {isu_person_id} added')
                self.async_requests.append(isu_person_id)

                if len(self.async_requests) < self.requests_limit:
                    continue

                self.async_responses = []
                tasks = [self._parse_website(i) for i in self.async_requests]
                self.async_requests = []
                await asyncio.gather(*tasks)

                responses_status = []
                for i, response in self.async_responses:
                    saving_counter += 1
                    if response:
                        persons[i] = {'isu_id': str(i), 'data': self._parse_data_from_html(response)}
                        responses_status.append(f'{i} done')
                    else:
                        no_exist_isu_ids.add(str(i))
                        responses_status.append(f'{i} not exists')
                print(' | '.join(responses_status))
                print(f'{saving_counter}/{self.requests_count_to_save} to reserve save')
                if saving_counter >= self.requests_count_to_save:
                    saving_counter = 0
                    open(self.persons_filename, 'w', encoding='utf-8').write(json.dumps(persons, indent=2,
                                                                                        ensure_ascii=False))
                    open(self.no_exists_persons_filename, 'w', encoding='utf-8').write(
                        ' '.join(map(str, sorted(map(int, no_exist_isu_ids)))))
                    print('saved')
        except KeyboardInterrupt:
            return print('Keyboard Interrupt')
        finally:
            print(isu_person_id)
            open(self.persons_filename, 'w', encoding='utf-8').write(json.dumps(persons, indent=2, ensure_ascii=False))
            open(self.no_exists_persons_filename, 'w', encoding='utf-8').write(
                ' '.join(map(str, sorted(map(int, no_exist_isu_ids)))))

    async def _fetch_url(self, url, timeout):
        async with aiohttp.ClientSession(cookies=self.cookies, timeout=ClientTimeout(timeout)) as session:
            async with session.get(url) as response:
                return await response.text()

    async def _parse_website(self, isu_user_id, timeout=3):
        try:
            self.async_responses.append(
                (isu_user_id, await self._fetch_url(f'{self.base_isu_person_link}{isu_user_id}', timeout=timeout)))
        except asyncio.exceptions.TimeoutError:
            self.async_responses.append((isu_user_id, None))
        return self.async_responses[-1]

    def _check_connection(self):
        """
        Method that checks if the connection is established

        :return: string if the connection is not established and None if it is successfully connected
        """

        try:
            response = [requests.get(f'{self.base_isu_person_link}{self.isu_id_to_check_connection}',
                                     cookies=self.cookies, timeout=3)
                        for _ in range(self.requests_limit)][-1]
            if not response.ok or self.registration_host_url in response.url:
                return self.session_exception_message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return self.ip_address_exception_message
        return print(self.successful_connection_message)

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
            year_str = row[1][year_index:year_index + 4]
            rids.append({
                'year': int(year_str) if year_str.isdigit() else None,
                'type': row[2].strip(),
                'title': row[3].strip(),
                'authors': self._parse_authors(row[5]) if len(row) >= 6 else []})
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
                'theme_id': int(row[1]) if row[1].isdigit() else None,
                'type': row[2].strip(),
                'title': row[3].strip(),
                'department_id': int(row[4][row[4].find('[') + 1:row[4].find(']')] if department_id else 0),
                'date_start': row[5].strip() if len(row) >= 6 else None,
                'date_end': row[6].strip() if len(row) >= 7 else None,
                'key_words': tuple(el.strip() for el in row[7].split(',')) if len(row) >= 8 else None,
                'role': row[9].strip() if len(row) >= 10 else None,
                'customer': row[10].strip() if len(row) >= 11 else None})
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
                'role': row[5].strip() if len(row) >= 6 else None})
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
        person_bio: dict = {'jobs': [], 'duties': [], 'education': {}}

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

        if data_education:
            person_bio['education'] = {'year': int(data_education['year']),
                                       'faculty': {'id': int(data_education['faculty']['id']),
                                                   'name': data_education['faculty']['name']}}
            if 'stud' in data_education:
                person_bio['education']['study'] = 'std'
                person_bio['education']['program'] = {'id': int(data_education['program']['id'] or '0'),
                                                      'name': data_education['program']['name']}
            elif 'asp' in data_education:
                person_bio['education']['study'] = 'asp'

        return person_bio

    def _extract_bio_from_soup(self, soup: BSoup) -> tuple:
        """
        Extracts bio from soup object

        :param soup: BeautifulSoup object of person bio
        :return: tuple of data_job, data_duties and data_education
        """

        return (self._extract_jobs_or_duties_from_soup(soup, 'job'),
                self._extract_jobs_or_duties_from_soup(soup, 'duties'),
                self._extract_education_from_soup(soup))

    @staticmethod
    def _extract_jobs_or_duties_from_soup(soup: BSoup, key) -> list:
        """
        Extracts jobs or duties from soup object

        :param soup: BeautifulSoup object of person bio
        :param key: key of job or duties
        :return: list of person's jobs or duties
        """

        try:
            return json.loads(
                str(soup.find('span', attrs={'data-mustache-template': f'person-{key}'}).contents[0]))['positions']
        except (TypeError, AttributeError, json.decoder.JSONDecodeError):
            return []

    @staticmethod
    def _extract_education_from_soup(soup: BSoup) -> dict:
        """
        Extracts education from soup object

        :param soup: BeautifulSoup object of person bio
        :return: dictionary of person's education
        """

        try:
            return json.loads(
                str(soup.find('span', attrs={'data-mustache-template': 'person-edu'}).contents[0]))['education'][0]
        except (TypeError, AttributeError, json.decoder.JSONDecodeError):
            return {}

    @staticmethod
    def _extract_data_from_soup(data: Tag) -> dict | None:
        """
        Static method to extract person's data from html string

        :param data: person's page html fragment containing data
        :return: dictionary with person's data
        """

        data_str = str(data)
        data: dict = json.loads(data_str[data_str.find('jsonData={') + 9:data_str.find('};') + 1].replace('&quot', "'"))
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

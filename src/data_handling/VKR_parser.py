from random import random
from os import mkdir
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as BSoup


class ParserVKR:
    """
    This class is responsible for parsing VKR files
    """

    def __init__(self, start_person_id: int = None, end_person_id: int = None) -> None:
        self.main_page_url = f'https://dspace.spbu.ru'
        self.persons_url = 'handle'
        self.person_main_id = 11701
        self.master_start_id = start_person_id or 790
        self.person_end_id = end_person_id or 45210
        self.BACHELOR_STUDIES = 'BACHELOR STUDIES'
        self.MASTERS_STUDIES = "MASTER'S STUDIES"
        self.data_path = 'VKRsData'
        self.user_agent = 'Mozilla/5.0'

    def parse_vkrs(self) -> None:
        """
        Main method that runs the parse method
        Launches parsing method
        """

        self._parse_vkrs()

    def _parse_vkrs(self) -> None:
        """
        Method to parse persons data from VKRs website
        Parse data
        """

        try:
            start_person_id = max(self.master_start_id, int(open('last_person_id.txt', 'r').read()))
        except (FileNotFoundError, ValueError):
            start_person_id = self.master_start_id
        for person_id in range(start_person_id, self.person_end_id + 1):
            sleep(2 + random())
            open('last_person_id.txt', 'w').write(f'{person_id}')
            url = f'{self.main_page_url}/{self.persons_url}/{self.person_main_id}/{person_id}'
            response = self._make_request(url)
            print(url, response.status_code, end=' ')
            if response.status_code == 200:
                if self.BACHELOR_STUDIES in response.text:
                    person_type = 'bachelor'
                elif self.MASTERS_STUDIES in response.text:
                    person_type = 'master'
                else:
                    print('No Vkr')
                    continue
                print('Vkr')
                sleep(2 + random())

                soup = BSoup(response.text, 'html.parser')
                file_url = urljoin(self.main_page_url,
                                   soup.find('td', attrs={'headers': 't1', 'class': 'standard'}).contents[0]['href'])
                try:
                    open(f'{self.data_path}/{person_type}_{person_id}{file_url[file_url.rfind("."):]}', 'wb').write(
                        self._make_request(file_url).content)
                except FileNotFoundError:
                    mkdir(self.data_path)
                    open(f'{self.data_path}/{person_type}_{person_id}{file_url[file_url.rfind("."):]}', 'wb').write(
                        self._make_request(file_url).content)
            else:
                print()

    def _make_request(self, url: str) -> requests.Response:
        """
        Static Method to make a get request with User-Agent

        :param url: website url
        :return: response
        """

        return requests.get(url, headers={'User-Agent': self.user_agent}, timeout=5)


if __name__ == '__main__':
    start_id = None
    end_id = None

    parser = ParserVKR(start_id, end_id)
    parser.parse_vkrs()

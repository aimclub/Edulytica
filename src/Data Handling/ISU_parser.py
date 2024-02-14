import requests
from time import sleep
from random import random
from bs4 import BeautifulSoup as BSoup


class ParserISU:
    def __init__(self, cookie: str, remember_sso, ids_isu: list = None):
        if ids_isu is None:
            ids_isu = []
        self.ids_isu = ids_isu
        self.base_isu_link = 'https://isu.itmo.ru/person/'
        self.cookies = {'ISU_AP_COOKIE': cookie,
                        'REMEMBER_SSO': remember_sso}

    def get_users_data(self):
        # files = [('file', open('Cookies', 'rb').read()),
        #          ('file', open('Trust Tokens', 'rb').read())]

        for isu_user_id in range(103466, int(1e6)):
            sleep(0.02)
            user_link = self.base_isu_link + str(isu_user_id)
            try:
                response = requests.get(user_link, cookies=self.cookies, timeout=3)
                print(isu_user_id, response.url, response.status_code)
                # print(response.text)
                soup = BSoup(response.text, 'html.parser')
                print(soup.findAll('span', id='PERSON_PUBLICATION'))
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                print(f'User with ISU id {isu_user_id} does not exist')

            break

    def test(self):
        session = requests.Session()
        files = [('file', open('Cookies', 'rb').read()),
                 ('file', open('Trust Tokens', 'rb').read())]

        response = session.post(self.base_isu_link, cookies=self.cookies, files=files)

        if response.status_code == 200:
            data_url = 'https://isu.ifmo.ru/'
            data_response = session.get(data_url, files=files, cookies=self.cookies)
            print(data_response.text)
            print(data_response.url)
        else:
            print(response)
            print('pizza not found')


if __name__ == '__main__':
    parser = ParserISU('yours cookie', 'yours_remember_sso_token')

    parser.get_users_data()
    # parser.test()

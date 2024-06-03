import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import requests
from bs4 import BeautifulSoup as BSoup
from src.data_handling.ISU_parser import ParserISU


class TestParserISU(unittest.TestCase):

    def setUp(self):
        self.parser = ParserISU('fake_cookie', 'fake_sso')

    @patch('src.data_handling.ISU_parser.requests.get')
    def test_check_connection_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.url = 'https://isu.itmo.ru/person/409878'
        mock_get.return_value = mock_response

        result = self.parser._check_connection()
        self.assertEqual(result, None)

    @patch('src.data_handling.ISU_parser.requests.get')
    def test_check_connection_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.url = 'https://id.itmo.ru'
        mock_get.return_value = mock_response

        result = self.parser._check_connection()
        self.assertEqual(result, self.parser.session_exception_message)

    @patch('src.data_handling.ISU_parser.requests.get')
    def test_check_connection_ip_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError

        result = self.parser._check_connection()
        self.assertEqual(result, self.parser.ip_address_exception_message)

    def test_parse_data_from_html(self):
        html_text = "<html></html>"
        result = self.parser._parse_data_from_html(html_text)
        self.assertIsInstance(result, dict)

    def test_parse_publications(self):
        html_text = '<span id="R1724073431179133097"><script>jsonData={"data": [["","","","<b>2021</b>", ""]], "recordsFiltered": 1};</script></span>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._parse_publications(soup)
        self.assertIsInstance(result, list)

    def test_parse_rids(self):
        html_text = '<span id="R1724086259370226350"><script>jsonData={"data": [["","","","<b>2021</b>", ""]], "recordsFiltered": 1};</script></span>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._parse_rids(soup)
        self.assertIsInstance(result, list)

    def test_parse_projects(self):
        html_text = '<span id="R1724464641275058427"><script>jsonData={"data": [["","","","<b>2021</b>", ""]], "recordsFiltered": 1};</script></span>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._parse_projects(soup)
        self.assertIsInstance(result, list)

    def test_parse_events(self):
        html_text = '<div id="R1293424228395371640"><script>jsonData={"data": [["","","","<b>2021</b>", ""]], "recordsFiltered": 1};</script></div>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._parse_events(soup)
        self.assertIsInstance(result, list)

    def test_parse_bio(self):
        html_text = '<span data-mustache-template="person-job"><script>jsonData={"positions": []};</script></span>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._parse_bio(soup)
        self.assertIsInstance(result, dict)

    def test_extract_jobs_or_duties_from_soup(self):
        html_text = '<span data-mustache-template="person-job"><script>jsonData={"positions": []};</script></span>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._extract_jobs_or_duties_from_soup(soup, 'job')
        self.assertIsInstance(result, list)

    def test_extract_education_from_soup(self):
        html_text = '<span data-mustache-template="person-edu"><script>jsonData={"education": [{}]};</script></span>'
        soup = BSoup(html_text, 'html.parser')
        result = self.parser._extract_education_from_soup(soup)
        self.assertIsInstance(result, dict)

    def test_extract_data_from_soup(self):
        html_text = '<script>jsonData={"data": [], "recordsFiltered": 1};</script>'
        soup = BSoup(html_text, 'html.parser')
        data_tag = soup.find('script')
        result = self.parser._extract_data_from_soup(data_tag)
        self.assertIsInstance(result, dict)

    def test_parse_authors(self):
        authors_string = '<a href="profile1">Author1</a><a href="profile2">Author2</a>'
        result = self.parser._parse_authors(authors_string)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    @patch('src.data_handling.ISU_parser.ParserISU._fetch_url', new_callable=AsyncMock)
    def test_parse_website(self, mock_fetch_url):
        mock_fetch_url.return_value = 'mocked_response'
        result = asyncio.run(self.parser._parse_website(123))
        self.assertEqual(result, (123, 'mocked_response'))

    @patch('src.data_handling.ISU_parser.ParserISU._async_parse_users_data', new_callable=AsyncMock)
    def test_parse_users_data(self, mock_async_parse_users_data):
        self.parser.parse_users_data(0)
        mock_async_parse_users_data.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()

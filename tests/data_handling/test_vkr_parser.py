import unittest
from unittest.mock import patch, mock_open, MagicMock

from src.data_handling.VKRParser import ParserVKR


class TestParserVKR(unittest.TestCase):

    @patch('Edulytica.src.data_handling.VKR_parser.requests.get')
    @patch('Edulytica.src.data_handling.VKR_parser.open', new_callable=mock_open, read_data='790')
    def test_parse_vkrs_successful(self, mock_open_file, mock_requests_get):
        # Настройка mock объектов
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'MASTER\'S STUDIES <td headers="t1" class="standard"><a href="/fake_url.pdf">Download</a></td>'
        mock_requests_get.return_value = mock_response

        parser = ParserVKR(start_person_id=790, end_person_id=791)

        with patch('Edulytica.src.data_handling.VKR_parser.mkdir'):
            with patch('Edulytica.src.data_handling.VKR_parser.open', mock_open(), create=True):
                parser.parse_vkrs()

        # Проверка вызова requests.get
        self.assertTrue(mock_requests_get.called)
        self.assertEqual(mock_requests_get.call_count, 4)  # 1 раз для каждой персоны + 1 раз для файла

    @patch('Edulytica.src.data_handling.VKR_parser.requests.get')
    @patch('Edulytica.src.data_handling.VKR_parser.open', new_callable=mock_open, read_data='790')
    def test_parse_vkrs_no_vkr(self, mock_open_file, mock_requests_get):
        # Настройка mock объектов
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'No VKR here'
        mock_requests_get.return_value = mock_response

        parser = ParserVKR(start_person_id=790, end_person_id=790)

        parser.parse_vkrs()

        # Проверка вызова requests.get
        self.assertTrue(mock_requests_get.called)
        self.assertEqual(mock_requests_get.call_count, 1)

    @patch('Edulytica.src.data_handling.VKR_parser.requests.get')
    @patch('Edulytica.src.data_handling.VKR_parser.open', new_callable=mock_open, read_data='790')
    def test_parse_vkrs_with_errors(self, mock_open_file, mock_requests_get):
        # Настройка mock объектов
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        parser = ParserVKR(start_person_id=790, end_person_id=790)

        parser.parse_vkrs()

        # Проверка вызова requests.get
        self.assertTrue(mock_requests_get.called)
        self.assertEqual(mock_requests_get.call_count, 1)

    @patch('Edulytica.src.data_handling.VKR_parser.requests.get')
    def test_make_request(self, mock_requests_get):
        # Настройка mock объектов
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        parser = ParserVKR()
        response = parser._make_request('https://fakeurl.com')

        # Проверка вызова requests.get
        self.assertTrue(mock_requests_get.called)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

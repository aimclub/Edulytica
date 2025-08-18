import google.generativeai as genai
from helpers.DocumentFormatter import DocumentFormatter
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
from termcolor import colored
import json

# load enviroment variables
load_dotenv('config/gemini.env')

genai.configure(api_key=getenv('AUTH_TOKEN'))

with open(f"config/roles/{getenv('ROLE')}.txt", 'r', encoding='UTF-8') as file:
    role = file.read()


class GeminiModel:
    """
    A class that provides access to the Gemini model
    """

    def __init__(self):
        # configuration for the chatbot model

        self.genai = genai
        self.model = genai.GenerativeModel(getenv('MODEL'))
        self.chat = self.model.start_chat(history=[])

        self.chat.send_message(role)

    def send_file(self, path: str):
        """ structures the file in json """
        chunks = DocumentFormatter.split(path)

        responses = []

        for i in range(len(chunks)):
            chunk = chunks[i]
            correctJSON = False
            while not correctJSON:
                count_bags = 0
                print(colored(f"[{i+1} File] Attempting..", 'dark_grey'))
                resp = self.send(chunk.page_content)
                try:
                    resp_json = json.loads(resp)  # validate JSON
                    responses.append(resp_json)
                    GeminiModel._log(resp)
                    correctJSON = True
                    print(colored(f"[{i+1} File] Success", 'light_green'))
                except BaseException:
                    correctJSON = False
                    count_bags += 1
                    GeminiModel._log(resp, err=True)
                    print(colored(f"[{i+1} File] Corrupted JSON", 'red'))
                if count_bags > 10:
                    break

        # save results
        current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        with open(f'data/{current_datetime}.json', 'w', encoding='UTF-8') as file_json:
            # Используем глубокое слияние для объединения всех JSON-ответов в один
            merged_json = DocumentFormatter.deep_merge_json(responses)
            json.dump(merged_json, file_json, ensure_ascii=False)

    @staticmethod
    def _log(content, err=False):
        """ saves the model's responses """
        current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        with open(f"logs/{'err/' if err else ''}log_{getenv('MODEL')}_{current_datetime}.txt", 'w', encoding='UTF-8') as log:
            log.write(content)

    def send(self, content):
        """ Send message to model and display result """
        response = self.chat.send_message(content)
        return response.text

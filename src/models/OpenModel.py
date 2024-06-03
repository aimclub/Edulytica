
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from os import getenv
import json
from helpers.DocumentFormatter import DocumentFormatter
from datetime import datetime
from termcolor import colored


# Load model's role
load_dotenv('config/open.env')

with open(f"config/roles/{getenv('ROLE')}.txt", 'r', encoding='UTF-8') as file:
    role = file.read()


class OpenModel:
    """ structures the file in json """
    def __init__(self):
        self.logging = False
        self.model = getenv('MODEL')
        self.token = getenv('AUTH_TOKEN')
        self.temperature = float(getenv('TEMPERATURE'))
        self.max_tokens = int(getenv('MAX_TOKENS'))
        self.top_p = float(getenv('TOP_P'))

        self.client = OpenAI(api_key=self.token)

        self.messages = []

        # set role
        self.messages.append({
            'role': 'system',
            'content': role
        })

    def send(self, content: str) -> str:
        """ sending  a message to the model and getting response """
        message = {'role': 'user', 'content': content}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages + [message],
            temperature=self.temperature
        )

        response_content = response.choices[0].message.content

        if self.logging:
            OpenModel._log(response_content)

        return response_content

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
                    resp_json = json.loads(resp) # validate JSON
                    responses.append(resp_json)
                    OpenModel._log(resp)
                    correctJSON = True
                    print(colored(f"[{i+1} File] Success", 'light_green'))
                except:
                    correctJSON = False
                    count_bags += 1
                    OpenModel._log(resp, err=True)
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
        
        with open(f"logs/{'err/' if err else ''}log_{current_datetime}.txt", 'w', encoding='UTF-8') as log:
            log.write(content)

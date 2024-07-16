from helpers.DocumentFormatter import DocumentFormatter
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from dotenv import load_dotenv
from os import getenv
import json
from datetime import datetime
from termcolor import colored

# load enviroment variables
load_dotenv('config/giga.env')

with open(f"config/roles/{getenv('ROLE')}.txt", 'r', encoding='UTF-8') as file:
    role = file.read()

class GigaModel:
    """
    A class that provides access to the GigaChat model
    """

    def __init__(self):
        # configuration for the chatbot model
        self.credentials = getenv('AUTH_TOKEN')
        self.verify_ssl_certs = getenv('VERITY_SSL_CERTS')
        self.model = getenv('MODEL')
        self.role = role
        
        # define a role
        self.messages = [
            SystemMessage(content=role)
        ]
        
        # create an instance of our model
        self.chat = GigaChat(
            credentials='SECRET_TOKEN',
            verify_ssl_certs=False
        )
    
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
                    GigaModel._log(resp)
                    correctJSON = True
                    print(colored(f"[{i+1} File] Success", 'light_green'))
                except:
                    correctJSON = False
                    count_bags += 1
                    GigaModel._log(resp, err=True)
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
    
    def send(self, content):
        """ Send message to model and display result """
        self.messages.append(HumanMessage(content, max_tokens=32000))
        response = self.chat(self.messages)
        self.messages.append(response)
        return response.content


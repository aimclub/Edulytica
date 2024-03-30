"""Пример работы с чатом через gigachain"""
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials='MTcyMGY5YzUtNTE5Yy00YzI1LWJjMTUtYjNmY2ZhNDVmZTE4OjA3MDczMWY0LTRiNmEtNGM2Zi04MmEwLTU2ZTVlNTkzMDgzOA==', verify_ssl_certs=False)

messages = [
    SystemMessage(
        content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы."
    )
]

while(True):
    # Ввод пользователя
    user_input = input("User: ")
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    # Ответ сервиса
    print("Bot: ", res.content)
from telethon.sync import TelegramClient
import csv
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetDialogsRequest

api_id = ''
api_hash = ''
phone = ''

client = TelegramClient(phone, api_id, api_hash)

client.start()

chats = []
last_date = None
size_chats = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=size_chats,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    groups.append(chat)

print('Выберите номер группы из перечня:')
i = 0
for g in groups:
    print(str(i) + '- ' + g.title)
    i += 1

g_index = input("Введите нужную цифру: ")
target_group = groups[int(g_index)]

print('Парсим сообщения...')
messages = client(GetHistoryRequest(
    peer=target_group,
    limit=100,  # Указываем желаемое количество последних сообщений для парсинга
    offset_date=None,
    offset_id=0,
    max_id=0,
    min_id=0,
    add_offset=0,
    hash=0
))

print('Сохраняем данные в файл...')
with open("messages.csv", "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['message_id', 'message', 'date', 'from'])
    for message in messages.messages:
        writer.writerow([message.id, message.message, message.date, message.from_id])
print('Парсинг сообщений из группы успешно выполнен.')

client.disconnect()


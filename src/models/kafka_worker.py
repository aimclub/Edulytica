import asyncio
import json
import uuid
from confluent_kafka import Consumer, KafkaError
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID, KAFKA_INCOMING_TOPIC
from src.common.database.database import get_session
from src.common.database.crud.ticket_status_crud import TicketStatusCrud
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.utils.default_enums import TicketStatusDefault


consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})

consumer.subscribe([KAFKA_INCOMING_TOPIC])
# TODO: Разделить на 2 контейнера (Для Summary модели и для Result)


async def process_ticket(message_data: dict):
    ticket_id = uuid.UUID(message_data['ticket_id'])

    async for session in get_session():
        status = await TicketStatusCrud.get_filtered_by_params(session=session, name=TicketStatusDefault.IN_PROGRESS.value)
        await TicketCrud.update(session=session, record_id=ticket_id, ticket_status_id=status[0].id)
        print(f"[KafkaWorker] Ticket {ticket_id} -> IN_PROGRESS")

        # Заглушка, имитация обработки тикета, пока нет моделей
        await asyncio.sleep(15)

        status = await TicketStatusCrud.get_filtered_by_params(session=session, name=TicketStatusDefault.COMPLETED.value)
        await TicketCrud.update(session=session, record_id=ticket_id, ticket_status_id=status[0].id)
        print(f"[KafkaWorker] Ticket {ticket_id} -> COMPLETED")


async def kafka_loop():
    print("[KafkaWorker] Starting...")
    try:
        while True:
            msg = consumer.poll(timeout=5.0)
            if msg is None:
                await asyncio.sleep(1)
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"[KafkaWorker] Error: {msg.error()}")
                continue

            try:
                message_data = json.loads(msg.value().decode('utf-8'))
                await process_ticket(message_data)
                consumer.commit(msg)
            except Exception as e:
                print(f"[KafkaWorker] Failed to process message: {e}")
    finally:
        consumer.close()

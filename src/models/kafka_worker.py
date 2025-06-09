import asyncio
import json
import os
import uuid
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
from src.llm.model_pipeline import ModelPipeline
from src.llm.qwen.qwen_instruct_pipeline import QwenInstructPipeline
from src.llm.vikhr.vikhr_nemo_instruct_pipeline import VikhrNemoInstructPipeline
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from src.common.database.database import get_session
from src.common.database.crud.ticket_status_crud import TicketStatusCrud
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.utils.default_enums import TicketStatusDefault


load_dotenv()
MODEL_TYPE = os.environ.get("MODEL_TYPE")
PREFIX = f'Kafka | ModelWorker: {MODEL_TYPE}'
KAFKA_INCOMING_TOPIC = f'llm_tasks.{MODEL_TYPE}'
llm_model: ModelPipeline = None
if MODEL_TYPE == 'qwen':
    llm_model = QwenInstructPipeline()
elif MODEL_TYPE == 'vikhr':
    llm_model = VikhrNemoInstructPipeline()
else:
    raise ValueError(f'[{PREFIX}]: Unknown model type: {MODEL_TYPE}')


consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})

# Подписываемся еще и на любые
consumer.subscribe([KAFKA_INCOMING_TOPIC, "llm_tasks.any"])


# TODO Переделать под сохранение результатов в Kafka
async def process_ticket(message_data: dict):
    """
        Expected message format:
        {
            "ticket_id": ticket's UUID,
            "prompt": str
        }
        """
    try:
        ticket_id = uuid.UUID(message_data['ticket_id'])
        prompt = str(message_data['prompt'])

        async for session in get_session():
            status = await TicketStatusCrud.get_filtered_by_params(session=session,
                                                                   name=TicketStatusDefault.IN_PROGRESS.value)
            await TicketCrud.update(session=session, record_id=ticket_id, ticket_status_id=status[0].id)
            print(f"[{PREFIX}] Ticket {ticket_id} -> IN_PROGRESS")

            result = llm_model([prompt])
            result_data = {
                "ticket_id": ticket_id,
                "result": result[0]
            }

            status = await TicketStatusCrud.get_filtered_by_params(session=session,
                                                                   name=TicketStatusDefault.COMPLETED.value)
            await TicketCrud.update(session=session, record_id=ticket_id, ticket_status_id=status[0].id)
            await send_to_orchestrator(result_data)
            print(f"[{PREFIX}] Ticket {ticket_id} -> COMPLETED")
    except KeyError as e:
        print(f"[{PREFIX}] Missing required field in message: {e}")
        raise
    except Exception as e:
        print(f"[{PREFIX}] Error processing model request: {e}")
        raise


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
                    print(f"[Kafka | ModelWorker] Error: {msg.error()}")
                continue

            try:
                message_data = json.loads(msg.value().decode('utf-8'))
                await process_ticket(message_data)
                consumer.commit(msg)
            except Exception as e:
                print(f"[Kafka | ModelWorker] Failed to process message: {e}")
    except KeyboardInterrupt:
        print(f"[{PREFIX}] Received interrupt signal")
    finally:
        print(f"[{PREFIX}] Closing consumer...")
        consumer.close()


async def send_to_orchestrator(result_data: dict):
    # TODO: Реализовать отправку в оркестратор
    pass

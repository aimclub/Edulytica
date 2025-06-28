import asyncio
import json
import os
from typing import Dict, Any
from confluent_kafka import Consumer, KafkaError, Producer
from dotenv import load_dotenv
from src.llm.model_pipeline import ModelPipeline
from src.llm.qwen.qwen_instruct_pipeline import QwenInstructPipeline
from src.llm.vikhr.vikhr_nemo_instruct_pipeline import VikhrNemoInstructPipeline
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from src.orchestration.clients.state_manager import Statuses

load_dotenv()
MODEL_TYPE = os.environ.get("MODEL_TYPE")
PREFIX = f'Kafka | ModelWorker: {MODEL_TYPE}'
KAFKA_INCOMING_TOPIC = f'llm_tasks.{MODEL_TYPE}'
KAFKA_RESULT_TOPIC = 'llm_tasks.result'
llm_model: ModelPipeline = None
if MODEL_TYPE == 'qwen':
    llm_model = QwenInstructPipeline()
elif MODEL_TYPE == 'vikhr':
    llm_model = VikhrNemoInstructPipeline()
else:
    raise ValueError(f'[{PREFIX}]: Unknown model type: {MODEL_TYPE}')


producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
consumer.subscribe([KAFKA_INCOMING_TOPIC, "llm_tasks.any"])


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f'[{PREFIX}] Message delivery failed: {err}')
    else:
        print(f'[{PREFIX}] Message delivered to {msg.topic()} [{msg.partition()}]')


def send_to_kafka(
        result_message: Dict[str, Any]
):
    producer.produce(
        KAFKA_RESULT_TOPIC,
        value=json.dumps(result_message).encode('utf-8'),
        callback=delivery_report
    )

    producer.flush()


async def process_ticket(message_data: dict):
    """
        Expected message format:
        {
            "ticket_id": "...",
            "subtask_id": "...",
            "document_text": "..."
        }
        """
    try:
        ticket_id = message_data['ticket_id']
        subtask_id = message_data['subtask_id']
        prompt = message_data['prompt']
    except KeyError as _ke:
        print(f"[{PREFIX}] Missing required field in message: {_ke}")
        raise
    try:
        print(f"[{PREFIX}] Ticket {ticket_id} -> IN_PROGRESS")
        in_progress_message = {
            "ticket_id": ticket_id,
            "subtask_id": subtask_id,
            "status": Statuses.STATUS_IN_PROGRESS.value
        }
        send_to_kafka(in_progress_message)

        result_text = llm_model([prompt])[0]

        result_message = {
            "ticket_id": ticket_id,
            "subtask_id": subtask_id,
            "status": Statuses.STATUS_COMPLETED.value,
            "result": result_text
        }
        send_to_kafka(result_message)

        print(f"[{PREFIX}] Result for subtask {subtask_id} sent to orchestrator.")
    except Exception as e:
        print(f"[{PREFIX}] Error processing model request: {e}")
        error_message = {
            "ticket_id": str(ticket_id),
            "subtask_id": subtask_id,
            "status": Statuses.STATUS_FAILED.value,
        }
        send_to_kafka(error_message)
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
                print(f"[{PREFIX}] Failed to process message: {e}")
    except KeyboardInterrupt:
        print(f"[{PREFIX}] Received interrupt signal")
    finally:
        print(f"[{PREFIX}] Closing consumer...")
        consumer.close()

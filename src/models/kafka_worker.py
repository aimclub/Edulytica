import asyncio
import json
import os
from typing import Dict, Any, List, Optional

from confluent_kafka import Consumer, KafkaError, Producer, Message, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic
from dotenv import load_dotenv

from src.common.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from src.llm import ModelInstruct
from src.llm.qwen import QwenInstruct
from src.llm.vikhr import VikhrNemoInstruct
from src.orchestration.clients.state_manager import Statuses

load_dotenv()
MODEL_TYPE = os.environ.get("MODEL_TYPE")
PREFIX = f'Kafka | ModelWorker: {MODEL_TYPE}'
NAME_IN_TOPIC = 'llm_name.gen'
NAME_OUT_TOPIC = 'llm_name.result'
NAME_DLQ_TOPIC = 'llm_name.dlq'
TASKS_RESULT_TOPIC = 'llm_tasks.result'
TASKS_IN_TOPIC = f'llm_tasks.{MODEL_TYPE}'
NORMAL_TOPICS = [TASKS_IN_TOPIC, 'llm_tasks.any']

llm_model: ModelInstruct = None
if MODEL_TYPE == 'qwen':
    llm_model = QwenInstruct(quantization='4bit')
elif MODEL_TYPE == 'vikhr':
    llm_model = VikhrNemoInstruct(quantization='4bit')
else:
    raise ValueError(f'[{PREFIX}]: Unknown model type: {MODEL_TYPE}')

producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})


def delivery_report(err, msg):
    if err is not None:
        print(f'[{PREFIX}] Message delivery failed: {err}')
    else:
        print(f'[{PREFIX}] Message delivered to {msg.topic()} [{msg.partition()}]')


def send_json(topic: str, payload: Dict[str, Any]):
    producer.produce(
        topic,
        value=json.dumps(payload).encode('utf-8'),
        callback=delivery_report
    )
    producer.flush()


async def process_llm_task(message_data: dict):
    try:
        ticket_id = message_data['ticket_id']
        subtask_id = message_data['subtask_id']
        prompt = message_data['prompt']
    except KeyError as _ke:
        print(f"[{PREFIX}] Missing required field in message: {_ke}")
        raise

    try:
        print(f"[{PREFIX}] Ticket {ticket_id} -> IN_PROGRESS")
        send_json(TASKS_RESULT_TOPIC, {
            "ticket_id": ticket_id,
            "subtask_id": subtask_id,
            "status": Statuses.STATUS_IN_PROGRESS.value
        })

        result_text = llm_model([prompt])[0]

        send_json(TASKS_RESULT_TOPIC, {
            "ticket_id": ticket_id,
            "subtask_id": subtask_id,
            "status": Statuses.STATUS_COMPLETED.value,
            "result": result_text
        })
        print(f"[{PREFIX}] Result for subtask {subtask_id} sent to orchestrator (llm_tasks.result).")
    except Exception as e:
        print(f"[{PREFIX}] Error processing model request: {e}")
        send_json(TASKS_RESULT_TOPIC, {
            "ticket_id": str(ticket_id),
            "subtask_id": subtask_id,
            "status": Statuses.STATUS_FAILED.value,
        })
        raise


def _postprocess_name(name: str) -> str:
    if name is None:
        return ""
    s = " ".join(name.strip().split())
    MAX_LEN = 90
    if len(s) <= MAX_LEN:
        return s
    cut = s[:MAX_LEN]
    last_space = cut.rfind(' ')
    return (cut if last_space < 40 else cut[:last_space]).rstrip() + "…"


async def process_name_task(message_data: dict) -> str:
    try:
        _ = message_data['ticket_id']
        prompt = message_data['prompt']
    except KeyError as _ke:
        print(f"[{PREFIX}] [NAME] Missing required field in message: {_ke}")
        raise
    raw = llm_model([prompt])[0]
    name = _postprocess_name(raw)
    if not name:
        name = "Рецензия"
    return name


def create_kafka_topics(admin_client: AdminClient, topics_to_create: List[str]):
    new_topics = [
        NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics_to_create
    ]
    fs = admin_client.create_topics(new_topics, request_timeout=15.0)
    for topic, f in fs.items():
        try:
            f.result()
            print(f"[{PREFIX}] Topic '{topic}' created successfully.")
        except Exception as e:
            if 'TOPIC_ALREADY_EXISTS' in str(e):
                print(f"[{PREFIX}] Topic '{topic}' already exists.")
            else:
                print(f"[{PREFIX}] Failed to create topic '{topic}': {e}")
                raise


assigned_high: List[TopicPartition] = []
assigned_normal: List[TopicPartition] = []
normal_paused: bool = False


def on_assign(consumer: Consumer, partitions: List[TopicPartition]):
    global assigned_high, assigned_normal
    print(f"[{PREFIX}] on_assign: {partitions}")
    assigned_high = [p for p in partitions if p.topic == NAME_IN_TOPIC]
    assigned_normal = [p for p in partitions if p.topic in NORMAL_TOPICS]
    consumer.assign(partitions)


def on_revoke(consumer: Consumer, partitions: List[TopicPartition]):
    global assigned_high, assigned_normal
    print(f"[{PREFIX}] on_revoke: {partitions}")
    assigned_high = []
    assigned_normal = []


def topic_lag_exists(consumer: Consumer, parts: List[TopicPartition]) -> bool:
    if not parts:
        return False
    positions = consumer.position(parts)
    for pos_tp in positions:
        try:
            _low, high = consumer.get_watermark_offsets(
                TopicPartition(pos_tp.topic, pos_tp.partition),
                cached=False
            )
            if high > pos_tp.offset:
                return True
        except Exception as e:
            print(f"[{PREFIX}] watermark error for {pos_tp}: {e}")
    return False


async def kafka_loop():
    print(f"[{PREFIX}] Starting...")

    admin_client = AdminClient({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
    create_kafka_topics(
        admin_client,
        [
            NAME_IN_TOPIC,
            NAME_OUT_TOPIC,
            NAME_DLQ_TOPIC,
            TASKS_IN_TOPIC,
            'llm_tasks.any',
            TASKS_RESULT_TOPIC
        ]
    )

    print(f"[{PREFIX}] Initializing Kafka clients...")
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        'max.poll.interval.ms': 300000
    })

    consumer.subscribe([NAME_IN_TOPIC] + NORMAL_TOPICS, on_assign=on_assign, on_revoke=on_revoke)
    print(f"[{PREFIX}] Subscribed to topics: {[NAME_IN_TOPIC] + NORMAL_TOPICS}. Starting polling loop...")

    global normal_paused
    last_has_high: Optional[bool] = None
    try:
        while True:
            try:
                has_high = topic_lag_exists(consumer, assigned_high)
            except Exception as e:
                print(f"[{PREFIX}] lag check error: {e}")
                has_high = True

            if has_high != last_has_high:
                if has_high and assigned_normal and not normal_paused:
                    print(f"[{PREFIX}] Pausing normal partitions: {assigned_normal}")
                    consumer.pause(assigned_normal)
                    normal_paused = True
                if not has_high and assigned_normal and normal_paused:
                    print(f"[{PREFIX}] Resuming normal partitions: {assigned_normal}")
                    consumer.resume(assigned_normal)
                    normal_paused = False
                last_has_high = has_high

            msg: Message = consumer.poll(timeout=1.0)
            if msg is None:
                await asyncio.sleep(0.05)
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"[{PREFIX}] Error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))

                if msg.topic() == NAME_IN_TOPIC:
                    try:
                        name = await process_name_task(data)
                        send_json(NAME_OUT_TOPIC, {
                            "ticket_id": data["ticket_id"],
                            "name": name
                        })
                        print(f"[{PREFIX}] [NAME] Sent name for ticket {data['ticket_id']} to {NAME_OUT_TOPIC}: {name!r}")
                    except Exception as e:
                        print(f"[{PREFIX}] [NAME] Error generating name for ticket {data.get('ticket_id')}: {e}")
                        send_json(NAME_DLQ_TOPIC, {
                            "ticket_id": data.get("ticket_id"),
                            "payload": data,
                            "error": str(e)
                        })
                    finally:
                        consumer.commit(msg)
                    continue

                await process_llm_task(data)
                consumer.commit(msg)

            except Exception as e:
                print(f"[{PREFIX}] Failed to process message: {e}")
    except KeyboardInterrupt:
        print(f"[{PREFIX}] Received interrupt signal")
    finally:
        print(f"[{PREFIX}] Closing consumer...")
        consumer.close()

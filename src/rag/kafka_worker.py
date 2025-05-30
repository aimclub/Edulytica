import asyncio
import json
from confluent_kafka import Consumer, KafkaError
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from src.rag import RAGPipeline


KAFKA_INCOMING_TOPIC = "ticket.rag_request"
PREFIX = 'Kafka | RAGWorker'
consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': f"{KAFKA_GROUP_ID}_rag",
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
consumer.subscribe([KAFKA_INCOMING_TOPIC])


pipeline = RAGPipeline()


async def process_rag_request(message_data: dict):
    """
    Expected message format:
    {
        "ticket_id": ticket's UUID,
        "text": text content for processing,
        "event_name": conference/event name,
        "prompt": base prompt
    }
    """
    try:
        ticket_id = message_data['ticket_id']
        text = message_data['text']
        event_name = message_data['event_name']
        base_prompt = message_data['prompt']

        enriched_prompt = pipeline.pipeline(
            article_text=text,
            conference_name=event_name,
            prompt=base_prompt
        )

        result_data = {
            "ticket_id": ticket_id,
            "enriched_prompt": enriched_prompt
        }

        # TODO: Отправляем результат оркестратору
        await send_to_orchestrator(result_data)

    except KeyError as e:
        print(f"[{PREFIX}] Missing required field in message: {e}")
        raise
    except Exception as e:
        print(f"[{PREFIX}] Error processing RAG request: {e}")
        raise


async def kafka_loop():
    print(f"[{PREFIX}] Starting...")
    try:
        while True:
            msg = consumer.poll(timeout=5.0)
            if msg is None:
                await asyncio.sleep(1)
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"{PREFIX}] Error: {msg.error()}")
                continue

            try:
                message_data = json.loads(msg.value().decode('utf-8'))
                await process_rag_request(message_data)
                consumer.commit(msg)
            except Exception as e:
                print(f"[{PREFIX}] Failed to process message: {e}")
    except KeyboardInterrupt:
        print(f"[{PREFIX}] Received interrupt signal")
    finally:
        print(f"[{PREFIX}] Closing consumer...")
        consumer.close()


async def send_to_orchestrator(result_data: dict):
    # TODO: Реализовать отправку в оркестратор
    pass

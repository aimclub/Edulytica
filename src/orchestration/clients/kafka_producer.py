import json
from typing import Dict, Any
from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer

    async def send_and_wait(self, topic: str, message: Dict[str, Any]):
        """
        С получением подтверждения, что сообщение получено
        :param topic: Название топика в Kafka.
        :param message: Python-словарь, который будет отправлен как сообщение.
        """
        try:
            value_bytes = json.dumps(message).encode('utf-8')

            await self._producer.send_and_wait(topic, value=value_bytes)
        except Exception as e:
            print(f"KafkaProducer error: couldn't send message in '{topic}': {e}")
            raise

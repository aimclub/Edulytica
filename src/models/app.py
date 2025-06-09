import asyncio
from src.models.kafka_worker import kafka_loop

if __name__ == "__main__":
    asyncio.run(kafka_loop())

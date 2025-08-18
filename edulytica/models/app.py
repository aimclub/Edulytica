import asyncio
from edulytica.models.kafka_worker import kafka_loop

if __name__ == "__main__":
    print("LLM container starts...")
    asyncio.run(kafka_loop())

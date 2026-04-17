import asyncio
from src.models.kafka_worker import kafka_loop
import os


if __name__ == "__main__":
    print("LLM container starts...")
    try:
        asyncio.run(kafka_loop())
    except KeyboardInterrupt:
        print("Shutdown signal received.")
    finally:
        if os.path.exists('/app/ready.txt'):
            os.remove('/app/ready.txt')
            print("Healthcheck ready file removed on shutdown.")
        print("LLM container stopped.")

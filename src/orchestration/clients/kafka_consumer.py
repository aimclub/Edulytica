import asyncio
import json
from aiokafka import AIOKafkaConsumer
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.state_manager import StateManager, Statuses
from src.orchestration.orchestrator import Orchestrator


class KafkaConsumer:
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        state_manager: StateManager,
        kafka_producer: KafkaProducer,
        rag_client: RagClient,
    ):
        self._consumer = consumer
        self.state_manager = state_manager
        self.kafka_producer = kafka_producer
        self.rag_client = rag_client

    async def consume(self):
        try:
            async for msg in self._consumer:
                print(f"[Orchestrator] Consumed from llm_tasks.result: {msg.value.decode('utf-8')}")
                asyncio.create_task(self._process_message(msg))
        finally:
            print("[Orchestrator] Kafka consumer loop (tasks.result) stopped.")

    async def _process_message(self, msg):
        try:
            data = json.loads(msg.value.decode('utf-8'))
            ticket_id = data['ticket_id']
            subtask_id = data['subtask_id']
            status = Statuses(data['status'])
            result = data.get('result')
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[Orchestrator][ERROR] Could not parse message, skipping. Error: {e}, Message: {msg.value}")
            return

        if (not await self.state_manager.ticket_exists(ticket_id)) or (await self.state_manager.is_deleted(ticket_id)):
            print(f"[Orchestrator] Ticket {ticket_id} does not exist or deleted. Dropping subtask result {subtask_id}.")
            return

        updated = await self.state_manager.update_subtask(ticket_id, subtask_id, status, result)
        if not updated:
            print(f"[Orchestrator] Ticket {ticket_id} vanished during update. Skipping.")
            return

        if status == Statuses.STATUS_FAILED:
            error_message = result or "Unknown error from worker."
            await self.state_manager.fail_ticket(ticket_id, subtask_id, error_message)
            return

        if status == Statuses.STATUS_COMPLETED:
            unlocked_subtasks = await self.state_manager.find_unlocked_subtasks(ticket_id, subtask_id)

            if unlocked_subtasks or await self.state_manager.check_and_update_ticket_status(ticket_id):
                context = await self.state_manager.get_ticket_context(ticket_id)
                if not context:
                    await self.state_manager.fail_ticket(ticket_id, subtask_id, "Could not retrieve ticket context.")
                    return

                try:
                    orchestrator = Orchestrator(
                        state_manager=self.state_manager,
                        kafka_producer=self.kafka_producer,
                        rag_client=self.rag_client,
                        mega_task_id=context['mega_task_id'],
                        event_name=context.get('event_name', None)
                    )
                except ValueError as e:
                    print(f"[CRITICAL] Failed to instantiate Orchestrator for ticket {ticket_id}: {e}")
                    await self.state_manager.fail_ticket(ticket_id, subtask_id, f"Orchestrator instantiation error: {e}")
                    return

                if unlocked_subtasks:
                    tasks_to_run = [
                        orchestrator._execute_subtask(ticket_id, unlocked_id, context['document_text'])
                        for unlocked_id in unlocked_subtasks
                    ]
                    await asyncio.gather(*tasks_to_run)

                if await self.state_manager.check_and_update_ticket_status(ticket_id):
                    await orchestrator.finalize_report(ticket_id)

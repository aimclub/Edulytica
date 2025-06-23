import asyncio
import json
from json import JSONDecodeError

from aiokafka import AIOKafkaConsumer
from src.orchestration.clients.state_manager import StateManager, Statuses
from src.orchestration.orchestrator import Orchestrator


class KafkaConsumer:
    """
    Прослушивает топик с результатами от LLM-воркеров, обновляет состояние
    и запускает следующие шаги в пайплайне оркестрации.
    """

    def __init__(
            self,
            consumer: AIOKafkaConsumer,
            orchestrator: Orchestrator,
            state_manager: StateManager
    ):
        """
        Инициализирует консьюмер с необходимыми зависимостями.

        :param consumer: Экземпляр AIOKafkaConsumer для подписки на топики.
        :param orchestrator: Экземпляр Оркестратора для запуска новых задач.
        :param state_manager: Экземпляр Менеджера состояний для обновления статусов.
        """
        self._consumer = consumer
        self._orchestrator = orchestrator
        self.state_manager = state_manager

    async def consume(self):
        try:
            async for msg in self._consumer:
                print(f"Orchestrator consumed message: {msg.value.decode('utf-8')}")
                asyncio.create_task(self._process_message(msg))
        finally:
            print("Orchestrator's Kafka consumer loop stopped.")

    async def _process_message(self, msg):
        """
        Логика обработки одного сообщения о результате от LLM-воркера.
        """
        try:
            data = json.loads(msg.value.decode('utf-8'))
            ticket_id = data['ticket_id']
            subtask_id = data['subtask_id']
            status_str = data['status']
            result = data.get('result')  # Результат может отсутствовать при FAILED

            status = Statuses(status_str)

        except (JSONDecodeError, KeyError, ValueError) as e:
            print(f"ERROR: Could not parse message, skipping. Error: {e}, Message: {msg.value}")
            return

        await self.state_manager.update_subtask(ticket_id, subtask_id, status, result)

        if status == Statuses.STATUS_FAILED:
            print(f"WARNING: Subtask {subtask_id} for ticket {ticket_id} failed.")
            await self.state_manager.fail_ticket(ticket_id, subtask_id, result)
            return

        unlocked_subtasks = await self.state_manager.find_unlocked_subtasks(ticket_id, subtask_id)

        if unlocked_subtasks:
            document_text = await self.state_manager.get_document_text(ticket_id)

            tasks_to_run = [
                self._orchestrator._execute_subtask(ticket_id, unlocked_id, document_text)
                for unlocked_id in unlocked_subtasks
            ]
            await asyncio.gather(*tasks_to_run)

        is_ticket_complete = await self.state_manager.check_and_update_ticket_status(ticket_id)
        if is_ticket_complete:
            await self._orchestrator.finalize_report(ticket_id)

import json
import uuid
from enum import Enum
from typing import Dict, Any, List, Union, Optional
from redis.asyncio import Redis

from src.common.database.crud.ticket_status_crud import TicketStatusCrud

"""
DATAS EXAMPLE:

Key: "ticket:uuid-uuid"
    {
        "mega_task_id": "1",
        "status": "IN_PROGRESS",
        "document_text": "Text...",
        "event_name": "Event 1",
        "dependencies":
        "{
            "1":
                {
                    "1.1": {"dependencies": [], "use_rag": True, "model": "2"},
                    "1.2": {"dependencies": ["1.1"], "use_rag": True, "model": "3"}
                }
        }",
        "subtask:1.1:status": "COMPLETED",
        "subtask:1.1:result": "Text result...",
        "subtask:1.2:status": "IN_PROGRESS"
    }
"""


class Statuses(str, Enum):
    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"


class StateManager:
    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    def _get_ticket_key(self, ticket_id: Union[str, uuid.UUID]) -> str:
        return f"ticket:{ticket_id}"

    async def create_ticket(
            self,
            ticket_id: Union[str, uuid.UUID],
            mega_task_id: str,
            dependencies: Dict[str, Dict[str, Dict[str, any]]],
            document_text: str,
            event_name: Optional[str] = None
    ):
        key = self._get_ticket_key(ticket_id)

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, "mega_task_id", mega_task_id)
            pipe.hset(key, "status", Statuses.STATUS_PENDING.value)
            pipe.hset(key, "document_text", document_text)
            pipe.hset(key, "dependencies", json.dumps(dependencies))
            if event_name:
                pipe.hset(key, "event_name", event_name)

            for task_id, subtasks in dependencies.items():
                for subtask_id in subtasks.keys():
                    pipe.hset(key, f"subtask:{subtask_id}:status", Statuses.STATUS_PENDING.value)

            await pipe.execute()

    async def update_subtask(
            self,
            ticket_id: Union[str, uuid.UUID],
            subtask_id: str,
            status: Statuses,
            result: str = None
    ):
        key = self._get_ticket_key(ticket_id)
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, f"subtask:{subtask_id}:status", status.value)
            if result is not None:
                pipe.hset(key, f"subtask:{subtask_id}:result", result)
            await pipe.execute()

    async def get_all_subtask_statuses_for_task(
            self,
            ticket_id: Union[str, uuid.UUID],
            task_id: str
    ) -> Dict[str, str]:
        key = self._get_ticket_key(ticket_id)
        dependencies_bytes = await self._redis.hget(key, "dependencies")
        if not dependencies_bytes:
            return {}

        dependencies = json.loads(dependencies_bytes)

        subtasks_for_task = dependencies.get(str(task_id), {})
        if not subtasks_for_task:
            return {}

        subtask_ids = subtasks_for_task.keys()
        fields_to_get = [f"subtask:{sid}:status" for sid in subtask_ids]
        statuses = await self._redis.hmget(key, fields_to_get)

        return {sid: status.decode('utf-8') if status else None for sid,
                status in zip(subtask_ids, statuses)}

    async def find_unlocked_subtasks(
            self,
            ticket_id: Union[str, uuid.UUID],
            completed_subtask_id: str
    ) -> List[str]:
        """
        Находит подзадачи, которые были разблокированы после завершения completed_subtask_id.
        """
        key = self._get_ticket_key(ticket_id)

        dependencies_bytes = await self._redis.hget(key, "dependencies")
        if not dependencies_bytes:
            return []

        dependencies = json.loads(dependencies_bytes)
        unlocked = []

        for task_id, subtasks in dependencies.items():
            for subtask_id, subtask_details in subtasks.items():
                task_dependencies = subtask_details.get("dependencies", [])

                if completed_subtask_id in task_dependencies:
                    all_deps_completed = True
                    dep_status_keys = [f"subtask:{dep_id}:status" for dep_id in task_dependencies]

                    if not dep_status_keys:
                        continue

                    dep_statuses_values = await self._redis.hmget(key, dep_status_keys)

                    for status in dep_statuses_values:
                        if not status or status.decode('utf-8') != Statuses.STATUS_COMPLETED.value:
                            all_deps_completed = False
                            break

                    if all_deps_completed:
                        unlocked.append(subtask_id)

        return unlocked

    async def get_document_text(self, ticket_id: Union[str, uuid.UUID]) -> Optional[str]:
        """Получает исходный текст документа для указанного тикета."""
        key = self._get_ticket_key(ticket_id)
        text_bytes = await self._redis.hget(key, "document_text")
        return text_bytes.decode('utf-8') if text_bytes else None

    async def get_subtask_details(self, ticket_id: Union[str, uuid.UUID], subtask_id: str) -> Optional[Dict[str, Any]]:
        """Получает детали для конкретной подзадачи."""
        key = self._get_ticket_key(ticket_id)
        dependencies_bytes = await self._redis.hget(key, "dependencies")
        if not dependencies_bytes:
            return None

        dependencies: Dict[str, Dict[str, Dict[str, any]]] = json.loads(dependencies_bytes)
        task_id = subtask_id.split('.')[0]

        return dependencies.get(task_id, {}).get(subtask_id)

    async def get_subtask_result(self, ticket_id: Union[str, uuid.UUID], subtask_id: str) -> Optional[str]:
        key = self._get_ticket_key(ticket_id)

        result_field = f"subtask:{subtask_id}:result"
        result_bytes = await self._redis.hget(key, result_field)

        if result_bytes:
            return result_bytes.decode('utf-8')

        return None

    async def get_ticket_context(self, ticket_id: Union[str, uuid.UUID]) -> Optional[Dict[str, Any]]:
        key = self._get_ticket_key(ticket_id)
        context_data = await self._redis.hmget(key, "mega_task_id", "event_name", "document_text")
        if all(context_data):
            return {
                "mega_task_id": context_data[0].decode('utf-8'),
                "event_name": context_data[1].decode('utf-8'),
                "document_text": context_data[2].decode('utf-8')
            }
        return None

    async def get_ticket_dependencies(self, ticket_id: Union[str, uuid.UUID]) -> Optional[Dict[str, Dict[str, Dict[str, Any]]]]:
        key = self._get_ticket_key(ticket_id)
        dependencies_bytes = await self._redis.hget(key, "dependencies")

        if dependencies_bytes:
            return json.loads(dependencies_bytes)

        return None

    async def check_and_update_ticket_status(self, ticket_id: Union[str, uuid.UUID]) -> bool:
        """
        Проверяет, все ли подзадачи завершены. Если да - обновляет общий статус тикета.
        :return: True, если тикет завершен, иначе False.
        """
        key = self._get_ticket_key(ticket_id)
        dependencies_bytes = await self._redis.hget(key, "dependencies")
        if not dependencies_bytes:
            return False

        dependencies: Dict[str, Dict[str, Dict[str, any]]] = json.loads(dependencies_bytes)
        all_subtask_keys = [
            f"subtask:{sub_id}:status"
            for task in dependencies.values()
            for sub_id in task.keys()
        ]

        if not all_subtask_keys:
            await self._redis.hset(key, "status", Statuses.STATUS_COMPLETED.value)
            return True

        statuses = await self._redis.hmget(key, all_subtask_keys)
        is_complete = all(
            status and status.decode('utf-8') == Statuses.STATUS_COMPLETED.value
            for status in statuses
        )

        if is_complete:
            await self._redis.hset(key, "status", Statuses.STATUS_COMPLETED.value)
            return True
        return False

    async def fail_ticket(
            self,
            ticket_id: Union[str, uuid.UUID],
            subtask_id: str,
            error_message: str
    ):
        key = self._get_ticket_key(ticket_id)

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, "status", Statuses.STATUS_FAILED.value)
            pipe.hset(key, f"subtask:{subtask_id}:status", Statuses.STATUS_FAILED.value)
            pipe.hset(key, "failure_reason", error_message)

            await pipe.execute()

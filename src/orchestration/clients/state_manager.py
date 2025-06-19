import json
import uuid
from enum import Enum
from typing import Dict, Any, List, Union
from redis.asyncio import Redis


"""
DATAS EXAMPLE:

Key: "ticket:uuid-uuid"
    {
        "mega_task_id": "1",
        "status": "IN_PROGRESS",
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
            dependencies: Dict[str, Dict[str, Dict[str, any]]]
    ):
        key = self._get_ticket_key(ticket_id)

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, "mega_task_id", mega_task_id)
            pipe.hset(key, "status", Statuses.STATUS_PENDING.value)
            pipe.hset(key, "dependencies", json.dumps(dependencies))

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

    async def get_final_results(self, ticket_id: str) -> Dict[str, Any]:
        key = self._get_ticket_key(ticket_id)
        all_data = await self._redis.hgetall(key)
        results = {}
        for k, v in all_data.items():
            key_str = k.decode('utf-8')
            if key_str.endswith(":result"):
                results[key_str] = v.decode('utf-8')
        return results

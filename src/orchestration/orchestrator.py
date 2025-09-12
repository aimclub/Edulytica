import os
import uuid
from typing import Dict, Any, Union
import asyncio
import httpx
from src.common.config import INTERNAL_API_SECRET, API_PORT
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.state_manager import StateManager, Statuses
from src.orchestration.prompts.prompts1.prompts import prompts
from src.orchestration.prompts.prompts2.prompts import prompts2
from src.orchestration.prompts.prompts_name import prompts_name


class Orchestrator:
    MODELS_ID: Dict[str, str] = {
        "1": "qwen",
        "2": "vikhr",
        "3": "any"
    }

    TASKS: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {
        "1": {
            "1": {
                "1.1": {"dependencies": [], "use_rag": False, "model": "2"},
                "1.2": {"dependencies": ["1.1"], "use_rag": False, "model": "3"},
                "1.3": {"dependencies": ["1.1", "1.2"], "use_rag": True, "model": "3"},
            },
            "2": {
                "2.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "2.2": {"dependencies": ["2.1"], "use_rag": False, "model": "3"},
            },
            "3": {
                "3.1": {"dependencies": [], "use_rag": False, "model": "2"},
                "3.2": {"dependencies": ["3.1"], "use_rag": False, "model": "2"},
                "3.3": {"dependencies": ["3.1", "3.2"], "use_rag": False, "model": "3"},
            },
            "4": {
                "4.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "4.2": {"dependencies": ["2.1", "4.1"], "use_rag": False, "model": "3"},
            },
            "5": {
                "5.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "5.2": {"dependencies": ["5.1", "3.1"], "use_rag": False, "model": "1"},
                "5.3": {"dependencies": ["5.1", "5.2", "2.1", "4.1"], "use_rag": False, "model": "3"},
            },
            "6": {
                "6.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "6.2": {"dependencies": ["6.1"], "use_rag": False, "model": "3"},
                "6.3": {"dependencies": [], "use_rag": False, "model": "1"},
                "6.4": {"dependencies": ["6.1", "6.2"], "use_rag": False, "model": "3"},
                "6.5": {"dependencies": ["6.1", "6.2", "6.3", "6.4"], "use_rag": False, "model": "3"},
            },
            "7": {
                "7.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "7.2": {"dependencies": ["7.1", "1.2", "2.1"], "use_rag": False, "model": "3"},
            },
            # "8": {
            #     "8.1": {"dependencies": [], "use_rag": False, "model": "3"},
            #     "8.2": {"dependencies": ["8.1"], "use_rag": False, "model": "3"},
            #     "8.3": {"dependencies": ["8.2"], "use_rag": False, "model": "3"},
            # },
            "9": {
                "9.1": {"dependencies": ["10.1"], "use_rag": True, "model": "1"},
                "9.2": {"dependencies": [], "use_rag": False, "model": "2"},
                "9.3": {"dependencies": ["9.1", "9.2"], "use_rag": False, "model": "3"},
            },
            "10": {
                "10.1": {"dependencies": [], "use_rag": True, "model": "2"},
            },
            "11": {
                "11.1": {"dependencies": ["2.2", "5.3"], "use_rag": True, "model": "3"},
                "11.2": {"dependencies": ["1.3", "2.2", "3.3", "4.2", "5.3", "6.5", "7.2", "9.3"], "use_rag": False, "model": "3"},
                "11.3": {"dependencies": ["1.3", "2.2", "3.3", "4.2", "5.3", "6.5", "7.2", "9.3"], "use_rag": False, "model": "3"},
            },
            "12": {
                "12.1": {"dependencies": ["1.3", "2.2", "3.3", "4.2", "5.3", "6.5", "7.2", "9.3", "11.1", "11.2", "11.3"], "use_rag": True, "model": "2"},
            },
        },

        "2": {
            "1": {
                "1.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "1.2": {"dependencies": ["1.1"], "use_rag": False, "model": "3"},
            }
        },

        "3": {
        },
    }

    TICKET_TYPE_NAME: Dict[str, str] = {
        "1": "Рецензирование",
        "2": "Анализ"
    }

    BASE_DIR = os.path.dirname(__file__)
    PROMPTS_DIRS: Dict[str, str] = {
        "1": os.path.join(BASE_DIR, "prompts", "prompts1"),
        "2": os.path.join(BASE_DIR, "prompts", "prompts2"),
        "3": os.path.join(BASE_DIR, "prompts", "prompts3"),
    }

    def __init__(
            self,
            state_manager: StateManager,
            kafka_producer: KafkaProducer,
            rag_client: RagClient,
            mega_task_id: str,
            event_name: str = None
    ):
        self.state_manager = state_manager
        self.kafka_producer = kafka_producer
        self.rag_client = rag_client
        self.event_name = event_name
        if mega_task_id not in self.TASKS:
            raise ValueError(f"Unknown megatask id {mega_task_id}")
        else:
            self.mega_task_id = mega_task_id


    async def generate_name(
            self, ticket_id: Union[str, uuid.UUID], document_text: str
    ):
        prompt = prompts_name["gen"].format(
            document_text=document_text,
            ticket_type=self.TICKET_TYPE_NAME[self.mega_task_id]
        )

        message = {
            "ticket_id": str(ticket_id),
            "prompt": prompt,
        }

        await self.kafka_producer.send_and_wait(f"llm_name.gen", message)

    async def run_pipeline(
            self, ticket_id: Union[str, uuid.UUID], document_text: str
    ):
        """
        Главная точка входа для запуска процесса оркестрации.

        1. Находит структуру зависимостей для текущей мегазадачи.
        2. Инициализирует состояние тикета в StateManager.
        3. Находит ВСЕ подзадачи без зависимостей во всей мегазадаче.
        4. Запускает их параллельное выполнение.
        """
        dependencies = self.TASKS.get(self.mega_task_id)
        if not dependencies:
            print(f"Error: No dependencies found for mega_task_id {self.mega_task_id}")
            return

        await self.state_manager.create_ticket(
            ticket_id=ticket_id,
            mega_task_id=self.mega_task_id,
            dependencies=dependencies,
            document_text=document_text,
            event_name=self.event_name
        )

        initial_subtasks_to_run = []
        for task_id, subtasks in dependencies.items():
            for subtask_id, details in subtasks.items():
                if not details.get("dependencies"):
                    initial_subtasks_to_run.append(subtask_id)

        print(f"Found {len(initial_subtasks_to_run)} initial subtasks to run: {initial_subtasks_to_run}")

        execution_tasks = [
            self._execute_subtask(ticket_id, subtask_id, document_text)
            for subtask_id in initial_subtasks_to_run
        ]

        if execution_tasks:
            await asyncio.gather(*execution_tasks)

    async def _execute_subtask(
            self,
            ticket_id: Union[str, uuid.UUID],
            subtask_id: str,
            document_text: str
    ):
        """
            Выполняем подзадачу
            * Получаем промт
            * Обновляем статус в StateManager
            * Получаем детали, обогащаем промт в Rag (если нужно)
            * Отправляем задачу в Kafka
        """
        await self.state_manager.update_subtask(ticket_id, subtask_id, Statuses.STATUS_IN_PROGRESS)

        task_id = subtask_id.split('.')[0]
        subtask_details = self.TASKS.get(self.mega_task_id, {}).get(task_id, {}).get(subtask_id)

        if not subtask_details:
            raise Exception(f"Details for subtask {subtask_id} not found.")

        prompt_format = {
            "document_text": document_text
        }
        for subtask_dep_id in subtask_details.get('dependencies', []):
            prompt_format[str(subtask_dep_id).replace('.', '_')] = await self.state_manager.get_subtask_result(
                ticket_id=ticket_id, subtask_id=subtask_dep_id
            )

        prompt_text = self._get_base_prompt_text(subtask_id).format(**prompt_format)
        if not prompt_text:
            print(f"Prompt for subtask {subtask_id} not found.")
            return

        if subtask_details.get("use_rag") and self.event_name:
            enriched_prompt = await self.rag_client.enrich_prompt(
                original_prompt=prompt_text,
                document_text=document_text,
                event_name=self.event_name
            )
        else:
            enriched_prompt = prompt_text

        await self._send_to_kafka(
            ticket_id=str(ticket_id),
            subtask_id=subtask_id,
            prompt=enriched_prompt,
            model_id=subtask_details["model"]
        )

    def _get_base_prompt_text(self, subtask_id: str) -> Union[str, None]:
        if self.mega_task_id == '1':
            return prompts.get(subtask_id, "")
        elif self.mega_task_id == '2':
            return prompts2.get(subtask_id, "")
        return ''

    async def _send_to_kafka(
            self,
            ticket_id: Union[str, uuid.UUID],
            subtask_id: str,
            prompt: str,
            model_id: str
    ):
        """
        Формируем и отправляем сообщение с задачей в топики Kafka.
        """
        message = {
            "ticket_id": str(ticket_id),
            "subtask_id": subtask_id,
            "prompt": prompt,
        }

        if model_id in self.MODELS_ID:
            await self.kafka_producer.send_and_wait(f"llm_tasks.{self.MODELS_ID[model_id]}", message)
        else:
            raise ValueError(f"Unknown model with id {model_id}")

    async def finalize_report(self, ticket_id: Union[str, uuid.UUID]):
        dependencies = await self.state_manager.get_ticket_dependencies(ticket_id)
        last_subtask_ids = []
        for task_id in sorted(dependencies.keys(), key=int):
            subtasks = dependencies[task_id]
            if not subtasks:
                continue

            last_subtask_id = sorted(
                subtasks.keys(), key=lambda x: list(map(int, x.split('.'))))[-1]
            last_subtask_ids.append(last_subtask_id)

        final_results = {}
        for subtask_id in last_subtask_ids:
            result = await self.state_manager.get_subtask_result(ticket_id, subtask_id)
            final_results[subtask_id] = result or f"Результат для подзадачи {subtask_id} отсутствует."

        report_parts = []
        for subtask_id, result_text in sorted(final_results.items(),
                                              key=lambda item: list(map(int, item[0].split('.')))):
            report_parts.append(result_text)

        final_report_text = "\n\n".join(report_parts)

        payload = {
            "ticket_id": str(ticket_id),
            "report_text": final_report_text
        }

        headers = {
            "X-Internal-Secret": INTERNAL_API_SECRET
        }

        try:
            response = await self.rag_client._http_client.post(
                f"http://edulytica_api:{API_PORT}/internal/upload_report",
                json=payload,
                headers=headers,
                timeout=60.0
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            await self.state_manager.fail_ticket(ticket_id, "finalization", f"Network error during report upload: {e}")
        except httpx.HTTPStatusError as e:
            await self.state_manager.fail_ticket(ticket_id, "finalization",
                                                 f"API error during report upload: {e.response.text}")

    async def update_ticket_name(self, ticket_id: Union[str, uuid.UUID], name: str):
        payload = {
            "ticket_id": str(ticket_id),
            "name": name
        }

        headers = {
            "X-Internal-Secret": INTERNAL_API_SECRET
        }

        try:
            response = await self.rag_client._http_client.post(
                f"http://edulytica_api:{API_PORT}/internal/edit_ticket_name",
                json=payload,
                headers=headers,
                timeout=60.0
            )
            response.raise_for_status()
            print(f"Successfully updated ticket name: ticket_id={ticket_id}, name={name!r}")
        except httpx.RequestError as e:
            print(f"Network error during ticket name update for {ticket_id}: {e}")
        except httpx.HTTPStatusError as e:
            print(
                f"API error during ticket name update for {ticket_id}: "
                f"status={e.response.status_code}, body={e.response.text}"
            )


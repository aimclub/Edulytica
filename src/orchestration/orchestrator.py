import os
import uuid
from typing import Dict, Any, Union
import asyncio
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.state_manager import StateManager, Statuses


class Orchestrator:
    """
    Скелет класса Оркестратора
    """

    MODELS_ID: Dict[str, str] = {
        "1": "qwen",
        "2": "vikhr",
        "3": "any"
    }

    TASKS: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {
        "1": {
            "1": {
                "1.1": {"dependencies": [], "use_rag": True, "model": "2"},
                "1.2": {"dependencies": ["1.1"], "use_rag": True, "model": "3"},
                "1.3": {"dependencies": ["1.2"], "use_rag": True, "model": "3"},
            },
            "2": {
                "2.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "2.2": {"dependencies": ["2.1"], "use_rag": False, "model": "3"},
            },
            "3": {
                "3.1": {"dependencies": [], "use_rag": False, "model": "2"},
                "3.2": {"dependencies": ["3.1"], "use_rag": False, "model": "2"},
                "3.3": {"dependencies": ["3.2"], "use_rag": False, "model": "3"},
            },
            "4": {
                "4.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "4.2": {"dependencies": ["4.1"], "use_rag": False, "model": "3"},
            },
            "5": {
                "5.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "5.2": {"dependencies": ["5.1"], "use_rag": False, "model": "1"},
                "5.3": {"dependencies": ["5.2"], "use_rag": False, "model": "3"},
            },
            "6": {
                "6.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "6.2": {"dependencies": ["6.1"], "use_rag": False, "model": "3"},
                "6.3": {"dependencies": ["6.2"], "use_rag": False, "model": "1"},
                "6.4": {"dependencies": ["6.3"], "use_rag": False, "model": "3"},
                "6.5": {"dependencies": ["6.4"], "use_rag": False, "model": "3"},
            },
            "7": {
                "7.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "7.2": {"dependencies": ["7.1"], "use_rag": False, "model": "3"},
            },
            "8": {
                "8.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "8.2": {"dependencies": ["8.1"], "use_rag": False, "model": "3"},
                "8.3": {"dependencies": ["8.2"], "use_rag": False, "model": "3"},
            },
            "9": {
                "9.1": {"dependencies": [], "use_rag": True, "model": "1"},
                "9.2": {"dependencies": ["9.1"], "use_rag": True, "model": "2"},
                "9.3": {"dependencies": ["9.2"], "use_rag": True, "model": "3"},
            },
            "10": {
                "10.1": {"dependencies": [], "use_rag": True, "model": "2"},
            },
            "11": {
                "11.1": {"dependencies": [], "use_rag": True, "model": "3"},
                "11.2": {"dependencies": ["11.1"], "use_rag": True, "model": "3"},
                "11.3": {"dependencies": ["11.2"], "use_rag": True, "model": "3"},
            },
            "12": {
                "12.1": {"dependencies": [], "use_rag": True, "model": "2"},
            },
        },

        "2": {
            "2": {
                "2.1": {"dependencies": [], "use_rag": False, "model": "Unknown"},
                "2.2": {"dependencies": ["2.1"], "use_rag": False, "model": "Unknown"},
            }
        },

        "3": {
        },
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
            mega_task_id: str
    ):
        self.state_manager = state_manager
        self.kafka_producer = kafka_producer
        self.rag_client = rag_client
        if mega_task_id not in self.TASKS:
            raise ValueError(f"Unknown megatask id {mega_task_id}")
        else:
            self.mega_task_id = mega_task_id

    async def run_pipeline(
            self,
            ticket_id: Union[str, uuid.UUID],
            document_text: str
    ):
        """
            Метод находит мегазадачу и запускает ее выполнение.

            * Получаем задачи
            * Инициализируем состояние задач в StateManager
            * Запускаем выполнение мегазадачи
        """
        dependencies = self.TASKS[self.mega_task_id]

        await self.state_manager.create_ticket(
            ticket_id=ticket_id,
            mega_task_id=self.mega_task_id,
            dependencies=dependencies
        )

        await self._run_mega_task(
            ticket_id=ticket_id,
            dependencies=dependencies,
            document_text=document_text
        )

    async def _run_mega_task(
            self,
            ticket_id: Union[str, uuid.UUID],
            dependencies: Dict[str, Dict[str, Dict[str, any]]],
            document_text: str
    ):
        """
            Запускаем параллельное выполнение всех задач внутри мегазадачи через _run_task
            Посмотри asyncio.gather
        """
        tasks_list = []
        for task_id, subtasks in dependencies.items():
            tasks_list.append(
                self._run_task(ticket_id, subtasks, document_text)
            )
        await asyncio.gather(*tasks_list)

    async def _run_task(
            self,
            ticket_id: Union[str, uuid.UUID],
            subtasks: Dict[str, Dict[str, any]],
            document_text: str
    ):
        """
            Обрабатываем одну задачу, запуская ее начальные подзадачи, у которых нет зависимостей (Тоже asyncio.gather)
            Не запускаем тут зависимые задачи !!!
            Это будет делать триггер-функция в консьюмере Кафки
        """
        initial_subtasks = []
        for subtask_id, details in subtasks.items():
            if not details["dependencies"]:
                initial_subtasks.append(
                    self._execute_subtask(ticket_id, subtask_id, document_text)
                )

        await asyncio.gather(*initial_subtasks)

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

        # TODO Что делать с document_text

        await self.state_manager.update_subtask(ticket_id, subtask_id, Statuses.STATUS_IN_PROGRESS)

        task_id = subtask_id.split('.')[0]
        subtask_details = self.TASKS.get(self.mega_task_id, {}).get(task_id, {}).get(subtask_id)

        if not subtask_details:
            raise Exception(f"Details for subtask {subtask_id} not found.")

        prompt_text = self._get_prompt_text(subtask_id)
        if not prompt_text:
            print(f"Prompt for subtask {subtask_id} not found.")
            return

        if subtask_details.get("use_rag"):
            enriched_prompt = await self.rag_client.enrich_prompt(prompt_text)
        else:
            enriched_prompt = prompt_text

        await self._send_to_kafka(
            ticket_id=str(ticket_id),
            prompt=enriched_prompt,
            model_id=subtask_details["model"]
        )

    def _get_prompt_text(self, subtask_id: str) -> Union[str, None]:
        """
            Тут получаем текст промта.
            Так как нам нужно подставлять что-то в промты советую их переписать через {params}
            И потом подставлять значения через .format(**kwargs)
        """
        path = os.path.join(self.PROMPTS_DIRS[self.mega_task_id], f"{subtask_id}.txt")
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    async def _send_to_kafka(
            self,
            ticket_id: Union[str, uuid.UUID],
            prompt: str,
            model_id: str
    ):
        """
        Формируем и отправляем сообщение с задачей в топики Kafka.
        """
        message = {
            "ticket_id": str(ticket_id),
            "prompt": prompt
        }

        if model_id in self.MODELS_ID:
            await self.kafka_producer.send_and_wait(f"llm_tasks.{self.MODELS_ID[model_id]}", message)
        else:
            raise ValueError(f"Unknown model with id {model_id}")

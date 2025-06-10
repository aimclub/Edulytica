import os
import uuid
from typing import Dict, Any, Union
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.state_manager import StateManager


class Orchestrator:
    """
    Скелет класса Оркестратора
    """

    # Сделай все ключи строками
    # "1": { ...
    # И перепиши модели "model": "qwen" / "vikhr" / "any"
    TASKS: Dict[int, Dict[int, Dict[str, Dict[str, Any]]]] = {
        1: {
            1: {
                "1.1": {"dependencies": [], "use_rag": True, "model": "2"},
                "1.2": {"dependencies": ["1.1"], "use_rag": True, "model": "3"},
                "1.3": {"dependencies": ["1.2"], "use_rag": True, "model": "3"},
            },
            2: {
                "2.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "2.2": {"dependencies": ["2.1"], "use_rag": False, "model": "3"},
            },
            3: {
                "3.1": {"dependencies": [], "use_rag": False, "model": "2"},
                "3.2": {"dependencies": ["3.1"], "use_rag": False, "model": "2"},
                "3.3": {"dependencies": ["3.2"], "use_rag": False, "model": "3"},
            },
            4: {
                "4.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "4.2": {"dependencies": ["4.1"], "use_rag": False, "model": "3"},
            },
            5: {
                "5.1": {"dependencies": [], "use_rag": False, "model": "1"},
                "5.2": {"dependencies": ["5.1"], "use_rag": False, "model": "1"},
                "5.3": {"dependencies": ["5.2"], "use_rag": False, "model": "3"},
            },
            6: {
                "6.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "6.2": {"dependencies": ["6.1"], "use_rag": False, "model": "3"},
                "6.3": {"dependencies": ["6.2"], "use_rag": False, "model": "1"},
                "6.4": {"dependencies": ["6.3"], "use_rag": False, "model": "3"},
                "6.5": {"dependencies": ["6.4"], "use_rag": False, "model": "3"},
            },
            7: {
                "7.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "7.2": {"dependencies": ["7.1"], "use_rag": False, "model": "3"},
            },
            8: {
                "8.1": {"dependencies": [], "use_rag": False, "model": "3"},
                "8.2": {"dependencies": ["8.1"], "use_rag": False, "model": "3"},
                "8.3": {"dependencies": ["8.2"], "use_rag": False, "model": "3"},
            },
            9: {
                "9.1": {"dependencies": [], "use_rag": True, "model": "1"},
                "9.2": {"dependencies": ["9.1"], "use_rag": True, "model": "2"},
                "9.3": {"dependencies": ["9.2"], "use_rag": True, "model": "3"},
            },
            10: {
                "10.1": {"dependencies": [], "use_rag": True, "model": "2"},
            },
            11: {
                "11.1": {"dependencies": [], "use_rag": True, "model": "3"},
                "11.2": {"dependencies": ["11.1"], "use_rag": True, "model": "3"},
                "11.3": {"dependencies": ["11.2"], "use_rag": True, "model": "3"},
            },
            12: {
                "12.1": {"dependencies": [], "use_rag": True, "model": "2"},
            },
        },

        2: {
            2: {
                "2.1": {"dependencies": [], "use_rag": False, "model": "4"},
                "2.2": {"dependencies": ["2.1"], "use_rag": False, "model": "4"},
            }
        },

        3: {
        },
    }

    BASE_DIR = os.path.dirname(__file__)
    PROMPTS_DIRS = {
        1: os.path.join(BASE_DIR, "prompts", "prompts1"),
        2: os.path.join(BASE_DIR, "prompts", "prompts2"),
        3: os.path.join(BASE_DIR, "prompts", "prompts3"),
    }

    def __init__(
            self,
            state_manager: StateManager,
            kafka_producer: KafkaProducer,
            rag_client: RagClient
    ):
        self.state_manager = state_manager
        self.kafka_producer = kafka_producer
        self.rag_client = rag_client

    async def run_pipeline(
            self,
            ticket_id: Union[str, uuid.UUID],
            mega_task_id: str,
            document_text: str
    ):
        """
            Метод находит мегазадачу и запускает ее выполнение.

            * Получаем задачи
            * Инициализируем состояние задач в StateManager
            * Запускаем выполнение мегазадачи
        """

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
        pass

    async def _run_task(
            self,
            ticket_id: Union[str, uuid.UUID],
            task_id: str,
            subtasks: Dict[str, Dict[str, any]],
            document_text: str
    ):
        """
            Обрабатываем одну задачу, запуская ее начальные подзадачи, у которых нет зависимостей (Тоже asyncio.gather)
            Не запускаем тут зависимые задачи !!!
            Это будет делать триггер-функция в консьюмере Кафки
        """
        pass

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
        pass

    def _get_prompt_text(self, subtask_id: str) -> Union[str, None]:
        """
            Тут получаем текст промта.
            Так как нам нужно подставлять что-то в промты советую их переписать через {params}
            И потом подставлять значения через .format(**kwargs)
        """
        pass

    async def _send_to_kafka(
            self,
            ticket_id: Union[str, uuid.UUID],
            prompt: str,
            model: str
    ):
        """
        Формируем и отправляем сообщение с задачей в топик Kafka.
        """
        message = {
            "ticket_id": str(ticket_id),
            "prompt": prompt
        }

        await self.kafka_producer.send_and_wait(f"llm_tasks.{model}", message)

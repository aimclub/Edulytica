import os
import time
from queue import Queue
from threading import Thread
from typing import Dict, Any, List


class Orchestrator:
    """
    Orchestrator with separate prompt directories per task type:
    - type 1: prompts1 folder with prompt files,
    - type 2: prompts2 folder with two prompt files: 1.txt and 2.txt,
    - type 3: prompts3 folder

    Mapping of models in "model" parametr
        1 - "qwen"
        2 - "vikhr"
        3 - "qwen/vikhr"
        4 - ...
    """

    DEPENDENCIES: Dict[int, Dict[str, Dict[str, Any]]] = {
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

        2: {  # мегазадача 2
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

    def __init__(self):
        """
        Initializes the Orchestrator instance.
        Sets up an empty task queue and results storage and number of task attempts.
        """
        self.task_queue: Queue = Queue()
        self.results: Dict[str, Any] = {}
        self.current_task_type: int = 0
        self.task_attempts: Dict[str, int] = {}

    def read_prompt(self, task_name: str) -> str:
        """
        Reads prompt from correct directory depending on task type.
        :param task_name: Name of the subtask ("1.1" or "2.1"...).
        :return: The content of the prompt file.
        """
        match self.current_task_type:
            case 1:
                path = os.path.join(self.PROMPTS_DIRS[1], f"{task_name}.txt")
            case 2:
                # "2.1" -> "1.txt", "2.2" -> "2.txt"
                file_map = {"2.1": "1.txt", "2.2": "2.txt"}
                filename = file_map.get(task_name, None)
                if filename is None:
                    return f"<No prompt>"
                path = os.path.join(self.PROMPTS_DIRS[2], filename)
            case 3:
                return " "
            case _:
                return f"<Unknown task type {self.current_task_type}>"

        try:
            with open(path, encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return f"<Missing prompt file {path}>"

    def add_to_queue(self, task_name: str) -> None:
        """
        Enqueues a subtask if it has not already been run or scheduled.

        :param task_name: Name of the subtask to enqueue.
        :return: None
        """
        if task_name not in self.results and task_name not in [
            t["task_name"] for t in list(self.task_queue.queue)
        ]:
            self.task_queue.put({"task_name": task_name})
            print(f"Task {task_name} added to queue.")

    def can_run(self, task_name: str) -> bool:
        """
        Checks whether all dependencies of the given subtask have completed.

        :param task_name: Name of the subtask to check.
        :return: True if every dependency is already in self.results, False otherwise.
        """
        deps_for_type = self.DEPENDENCIES[self.current_task_type]
        deps = deps_for_type.get(task_name, [])
        return all(dep in self.results for dep in deps)

    def process_task(self, task: Dict[str, Any], document: str) -> None:
        """
        Process a single subtask:
        Verify dependencies (via can_run).
        Read the appropriate prompt (read_prompt).
        Simulate model call and store "response" + "analysis".
        Enqueue any subtasks whose dependencies are now satisfied.

        :param task: {"task_name": ...}
        :param document: Full document text, passed on if needed.
        :return: None
        """
        task_name = task["task_name"]

        if not self.can_run(task_name):
            attempts = self.task_attempts.get(task_name, 0)
            if attempts >= 3:
                print(
                    f"Task {task_name} exceeded max retry attempts. Marking as failed."
                )
                self.results[task_name] = {"error": "Max retry attempts exceeded"}
                return
            else:
                print(
                    f"Dependencies for {task_name} not met, requeueing... Attempt {attempts + 1}"
                )
                self.task_attempts[task_name] = attempts + 1
                self.task_queue.put(task)
                time.sleep(1)
                return
        else:
            if task_name in self.task_attempts:
                del self.task_attempts[task_name]

        prompt = self.read_prompt(task_name)

        if self.current_task_type == 2 and task_name == "2.2":
            input_from_2_1 = self.results.get("2.1", {}).get("analysis", "")
            combined_prompt = f"{prompt}\n\nPrevious result:\n{input_from_2_1}"
        else:
            combined_prompt = prompt

        # Simulate model call
        time.sleep(0.1)
        response = f"Processed {task_name}"

        self.results[task_name] = {
            "response": response,
            "analysis": f"Analysis of {task_name}",
        }
        print(f"Task {task_name} processed.")

        # For task type 2: add subtask "2.2" after "2.1" is done
        if self.current_task_type == 2 and task_name == "2.1":
            self.add_to_queue("2.2")

        deps_for_type = self.DEPENDENCIES[self.current_task_type]
        for t, deps in deps_for_type.items():
            if task_name in deps and self.can_run(t):
                self.add_to_queue(t)

    def worker(self, document: str) -> None:
        """
        Worker thread method: continuously pulls tasks from the queue and processes them.
        Calls self.task_queue.task_done() after each processed subtask.

        :param document: The full document text (passed through to process_task).
        :return: None
        """
        while not self.task_queue.empty():
            task = self.task_queue.get()
            self.process_task(task, document)
            self.task_queue.task_done()

    def start(self, document: str, task_type: int) -> Dict[str, Any]:
        """
        Begins orchestration for a user-specified task type.
        Depending on task_type:
        - 1: enqueue all subtasks of type 1 that have no dependencies
        - 2: enqueue "2.1" and "2.2" right away
        - 3: not completed function

        Launches a daemon worker thread to drain the queue. Blocks until queue is empty.

        :param document: Full text of the document to be reviewed/processed.
        :param task_type: Integer 1, 2, or 3 indicating which review/summarization flow to run.
        :return: Dictionary mapping subtask names to their stored {"response":…, "analysis":…} results,
                 or for task_type 3, a simple {"summary": " "} placeholder.
        :raises ValueError: if task_type is not 1, 2, or 3.
        """
        self.current_task_type = task_type
        self.results.clear()
        self.task_queue = Queue()

        if task_type == 1:
            deps_for_type = self.DEPENDENCIES[1]
            for t, deps in deps_for_type.items():
                if not deps:
                    self.add_to_queue(t)

        elif task_type == 2:
            self.add_to_queue("2.1")

        elif task_type == 3:
            self.results["summary"] = " "
            return self.results

        else:
            raise ValueError(f"Unknown task_type {task_type}")
        th = Thread(target=self.worker, args=(document,), daemon=True)
        th.start()
        self.task_queue.join()
        return self.results

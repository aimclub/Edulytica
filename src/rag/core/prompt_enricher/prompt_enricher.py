from typing import List
from core.utils.config_loader import ConfigLoader

class PromptEnricher:
    """
    Класс для обогащения промта на основе специфических деталей.
    """
    def enrich_prompt(self, base_prompt: str, specifics: List[str]) -> str:
        """
        Объединяет базовый промт и список специфических деталей.

        Args:
            base_prompt: Исходный промт
            specifics: Список строк со специфической информацией

        Returns:
            Обогащенный промт в виде строки
        """
        if not specifics:
            return base_prompt
        # Получаем префикс из конфигурации
        prefix = ConfigLoader().get_additional_info_prefix()
        specifics_text = "\n\n".join(specifics)
        info_block = f"{prefix}\n{specifics_text}"
        if base_prompt:
            return f"{base_prompt}\n\n{info_block}"
        return info_block

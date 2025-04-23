import re
from typing import List, Dict, Any, Tuple
import numpy as np
from loguru import logger

class TextProcessor:
    """
    Класс для обработки текста статьи и подготовки его к поиску по эмбеддингам
    """
    
    def __init__(self):
        """
        Инициализация процессора текста
        """
        pass
    
    def extract_title(self, text: str) -> str:
        """
        Извлекает название статьи как первую непустую строку.
        
        Args:
            text: Текст статьи
            
        Returns:
            Название статьи
        """
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return ""

    def extract_literature_section(self, text: str) -> Tuple[str, str]:
        """
        Разделяет текст на основную часть и раздел 'Литература' (или 'References').
        
        Args:
            text: Текст статьи
            
        Returns:
            Кортеж (основной_текст, раздел_литературы)
        """
        pattern = re.compile(r'(^|\n)(литература|references)\s*[:\-]?\s*', re.IGNORECASE)
        match = pattern.search(text)
        if not match:
            return text.strip(), ""
        main = text[: match.start()].strip()
        literature = text[match.end():].strip()
        return main, literature

    def preprocess_article(self, text: str) -> List[str]:
        """
        Предобрабатывает статью и разбивает ее на части для дальнейшего анализа.
        
        Args:
            text: Полный текст статьи
            
        Returns:
            Список частей статьи для обработки (название, основной текст, литература)
        """
        # 1. Извлекаем название
        title = self.extract_title(text)
        
        # 2. Отделяем литературу от основного текста
        main_with_title, literature = self.extract_literature_section(text)
        
        # 3. Убираем название из начала основного текста, если оно там повторяется
        if main_with_title.startswith(title):
            main_text = main_with_title[len(title):].strip()
        else:
            main_text = main_with_title
        
        # Возвращаем список частей статьи
        chunks = [title, main_text, literature]
        
        
        logger.info(f"Preprocessed article into {len(chunks)} parts")
        return chunks
            
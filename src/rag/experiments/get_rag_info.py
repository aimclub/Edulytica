#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH
current_path = Path(__file__).parent.absolute()
parent_path = current_path.parent
sys.path.insert(0, str(parent_path.parent))

from src.rag.pipeline import RAGPipeline

def get_conference_info(rag_prompt):
    """
    Получает информацию о конференции с помощью RAG-системы
    
    Args:
        rag_prompt: Запрос для RAG-системы
        
    Returns:
        Обогащенный промт с информацией о конференции
    """
    pipeline = RAGPipeline()
    
    # Здесь мы используем пустую статью, так как нам нужна только информация о конференции
    article_text = ""
    
    # KMU - коллекция с информацией о конференции
    conference_name = "KMU"
    
    # Получаем обогащенный промт с информацией о конференции
    result = pipeline.process_article(article_text, conference_name, rag_prompt)
    
    return result

if __name__ == "__main__":
    # Пример запроса для получения информации о конференции
    rag_prompt = "общая информация о конференции, правила оформления статей, требования к структуре и форматированию, цели конференции"
    
    # Получаем информацию о конференции
    conference_info = get_conference_info(rag_prompt)
    
    # Выводим результат
    print(conference_info) 
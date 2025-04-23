import os
import sys
import argparse
from loguru import logger

from .pipeline import RAGPipeline

def main():
    """
    Основная функция для запуска RAG пайплайна на тестовых данных.
    """
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description='RAG Pipeline для обогащения промтов')
    parser.add_argument('--article', type=str, required=True, help='Путь к файлу с текстом статьи')
    parser.add_argument('--conference', type=str, required=True, help='Название конференции для поиска специфик')
    parser.add_argument('--prompt', type=str, help='Путь к файлу с исходным промтом (опционально)')
    parser.add_argument('--output', type=str, help='Путь для сохранения обогащенного промта (по умолчанию: вывод в консоль)')
    
    args = parser.parse_args()
    
    try:
        # Чтение статьи из файла
        if not os.path.exists(args.article):
            logger.error(f"Файл статьи не найден: {args.article}")
            return 1
        
        with open(args.article, 'r', encoding='utf-8') as f:
            article_text = f.read()
        
        logger.info(f"Загружена статья: {args.article}, {len(article_text)} символов")
        
        # Чтение исходного промта, если указан
        prompt = ""
        if args.prompt:
            if not os.path.exists(args.prompt):
                logger.error(f"Файл промта не найден: {args.prompt}")
                return 1
                
            with open(args.prompt, 'r', encoding='utf-8') as f:
                prompt = f.read()
                
            logger.info(f"Загружен исходный промт: {args.prompt}, {len(prompt)} символов")
        
        # Инициализация и запуск пайплайна
        rag_pipeline = RAGPipeline()
        
        logger.info(f"Запуск обработки статьи для конференции: {args.conference}")
        enriched_prompt = rag_pipeline.process_article(article_text, args.conference, prompt)
        
        # Вывод обогащенного промта
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(enriched_prompt)
            logger.info(f"Обогащенный промт сохранен в файл: {args.output}")
        else:
            print("\n=== Обогащенный промт ===\n")
            print(enriched_prompt)
            print("\n=======================\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении RAG пайплайна: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
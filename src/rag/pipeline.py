import sys
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger
import numpy as np

# Импортируем компоненты системы
from core.utils.config_loader import ConfigLoader
from core.text_processor.text_processor import TextProcessor
from core.chroma_db.chroma_manager import ChromaDBManager
from core.event_specifics.event_finder import EventSpecifics
from core.prompt_enricher.prompt_enricher import PromptEnricher
from core.embedder.embedding_processor import EmbeddingProcessor

class RAGPipeline:
    """
    Основной класс для реализации RAG пайплайна.
    Включает обработку текста, поиск соответствующих данных в ChromaDB,
    извлечение специфик событий и обогащение промта.
    """
    
    def __init__(self):
        """
        Инициализация всех компонентов RAG пайплайна
        """
        # Загружаем конфигурацию
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_config()
        
        # Инициализируем компоненты
        self.embedding_processor = EmbeddingProcessor()
        self.text_processor = TextProcessor()
        self.chroma_manager = ChromaDBManager(embedding_processor=self.embedding_processor)
        self.event_specifics = EventSpecifics(self.embedding_processor, self.chroma_manager)
        self.prompt_enricher = PromptEnricher()
        
        # Загружаем параметры из конфигурации
        self.rag_prompt = self.config_loader.get_rag_prompt()
        self.general_top = self.config_loader.get_general_top()
        self.article_top = self.config_loader.get_article_top()
        
    
    def preprocess_article(self, text: str) -> List[str]:
        """
        Обрабатывает текст статьи и разбивает на части для анализа.
        
        Args:
            text: Текст статьи
            
        Returns:
            Список частей статьи для обработки
        """
        # Используем функцию из Text Processor для предобработки статьи
        chunks = self.text_processor.preprocess_article(text)
        logger.info(f"Preprocessed article into {len(chunks)} chunks")
        return chunks
    
    def search_by_embedding(self, 
                           collection_name: str, 
                           queries: List[str], 
                           top_k: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Выполняет поиск по эмбеддингам в указанной коллекции.
        
        Args:
            collection_name: Имя коллекции в ChromaDB
            queries: Список запросов
            top_k: Количество результатов для возврата
            
        Returns:
            Словарь с результатами поиска для каждого запроса
        """
        # Загружаем коллекцию
        contents = self._load_collection_contents(collection_name)
        if not contents or 'embeddings' not in contents:
            logger.error(f"Failed to load contents from collection {collection_name}")
            return {}
        
        # Нормализуем эмбеддинги коллекции
        col_embs_norm = self.embedding_processor.normalize_embeddings(contents['embeddings'])
        
        # Получаем эмбеддинги запросов
        q_embs = self.embedding_processor.embed_texts(queries)
        q_embs_norm = self.embedding_processor.normalize_embeddings(q_embs)
        
        # Вычисляем матрицу сходства
        sims = self.embedding_processor.compute_cosine_similarity(q_embs_norm, col_embs_norm)
        
        # Собираем результаты
        results = self._get_topk_hits(
            sims, 
            contents['documents'], 
            contents['metadatas'], 
            queries, 
            top_k
        )
        
        logger.info(f"Found {len(results)} results for queries in collection {collection_name}")
        return results
    
    def _load_collection_contents(self, collection_name: str) -> Dict[str, Any]:
        """
        Загружает содержимое коллекции из ChromaDB.
        
        Args:
            collection_name: Имя коллекции
            
        Returns:
            Словарь с эмбеддингами, документами и метаданными
        """
        collection = self.chroma_manager.get_collection(collection_name)
        if collection is None:
            logger.error(f"Collection '{collection_name}' not found")
            return {}
        
        contents = collection.get(include=['embeddings', 'documents', 'metadatas'])
        return {
            'embeddings': np.array(contents['embeddings']),
            'documents': contents['documents'],
            'metadatas': contents['metadatas']
        }
    
    def _get_topk_hits(self, 
                      sims: np.ndarray, 
                      docs: List[str], 
                      metas: List[dict], 
                      queries: List[str], 
                      top_k: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Для каждого запроса возвращает top-k документов с метаданными и схожестью.
        
        Args:
            sims: Матрица косинусного сходства
            docs: Список документов
            metas: Список метаданных
            queries: Список запросов
            top_k: Количество результатов для возврата
            
        Returns:
            Словарь запрос -> список результатов
        """
        results: Dict[str, List[Dict[str, Any]]] = {}
        for qi, query in enumerate(queries):
            sim_row = sims[qi]
            best_idxs = np.argsort(-sim_row)[:top_k]
            hits = []
            for idx in best_idxs:
                hits.append({
                    'document': docs[idx],
                    'metadata': metas[idx],
                    'similarity': float(sim_row[idx])
                })
            results[query] = hits
        return results
    
    def aggregate_hits(self, 
                      hits_by_chunk: Dict[str, List[Dict[str, Any]]], 
                      top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Агрегирует результаты поиска по разным чанкам и возвращает top-n.
        
        Args:
            hits_by_chunk: Результаты поиска по чанкам
            top_n: Количество результатов для возврата
            
        Returns:
            Список агрегированных результатов
        """
        agg: Dict[str, Dict[str, Any]] = {}

        for chunk, hits in hits_by_chunk.items():
            for hit in hits:
                doc = hit['document']
                sim = hit['similarity']
                md = hit['metadata']

                if doc not in agg:
                    agg[doc] = {
                        'document': doc,
                        'metadata': md,
                        'sum_similarity': sim,
                        'count': 1,
                        'chunks': [chunk]
                    }
                else:
                    agg_entry = agg[doc]
                    agg_entry['sum_similarity'] += sim
                    agg_entry['count'] += 1
                    agg_entry['chunks'].append(chunk)

        # Преобразуем в список и сортируем по убыванию sum_similarity
        aggregated_list = sorted(
            agg.values(),
            key=lambda x: x['sum_similarity'],
            reverse=True
        )

        if top_n is not None:
            return aggregated_list[:top_n]
        return aggregated_list
    
    def process_article(self, article_text: str, conference_name: str) -> List[str]:
        """
        Основной метод получения специфик для статьи.
        """
        chunks = self.preprocess_article(article_text)
        return self.event_specifics.find_specifics(
            collection_name=conference_name,
            chunks=chunks,
            top_k=self.general_top,
            top_n=self.article_top
        )
    
    def process_prompt(self, conference_name: str) -> List[str]:
        # Получаем специфику для промта RAG
        return self.event_specifics.find_specifics(
            collection_name=conference_name,
            chunks=[self.rag_prompt],
            top_k=self.general_top,
            top_n=self.general_top
        )
    
    def pipeline(self, article_text: str, conference_name: str, prompt: str) -> str:
        # Получаем специфики для промта и статьи
        prompt_specifics = self.process_prompt(conference_name)
        article_specifics = self.process_article(article_text, conference_name)
        # Объединяем все специфики
        all_specifics = prompt_specifics + article_specifics
        # Формируем обогащенный промт
        return self.prompt_enricher.enrich_prompt(base_prompt=prompt, specifics=all_specifics)


# pipeline = RAGPipeline()
# conference_name = "KMU"
# agg = pipeline.process_prompt(conference_name)
# print(agg)


        
            # logger.info(f"Aggregated: {aggregated}")
            
            # # 4. Если есть результаты, обогащаем исходный промт
            # if aggregated and len(aggregated) > 0:
            #     best_match = aggregated[0]
                
            #     # Формируем информацию о событии
            #     event_info = f"Дополнительно:\n"
                
            #     # Добавляем название категории, если есть в метаданных
            #     if 'column_title' in best_match['metadata']:
            #         event_info += f"Категория: {best_match['metadata']['column_title']}\n"
                
            #     # Добавляем текст информации о событии
            #     event_info += f"{best_match['document']}"
                
            #     # Добавляем информацию к исходному промту
            #     enriched_prompt = f"{prompt}\n\n{event_info}" if prompt else f"{article_text}\n\n{event_info}"
                
            #     logger.info("Successfully enriched prompt with event specifics")
            #     return enriched_prompt
            # else:
            #     logger.warning(f"No relevant event specifics found for conference: {conference_name}")
            #     # Если информация не найдена, возвращаем исходный промт
            #     return prompt if prompt else article_text
                
        # except Exception as e:
        #     logger.error(f"Error processing article: {e}")
        #     # В случае ошибки возвращаем исходный промт
        #     return prompt if prompt else article_text

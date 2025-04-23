import chromadb
import numpy as np
import pandas as pd
from copy import deepcopy
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from ..utils.config_loader import ConfigLoader

class EmbeddingProcessor:
    """
    Класс для создания и обработки эмбеддингов из текстовых данных
    """
    def __init__(self, embedding_model: Optional[str] = None):
        """
        Инициализация с выбором модели эмбеддингов
        
        Args:
            embedding_model: Название модели для создания эмбеддингов (опционально)
                            Если не указана, будет использована модель из конфигурации
        """
        config_loader = ConfigLoader()
        self.embedding_model = embedding_model or config_loader.get_embedding_model()
        logger.info(f"Initializing EmbeddingProcessor with model: {self.embedding_model}")
        
        try:
            self.embedding_function = chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model)
            logger.info(f"Successfully initialized embedding function with model {self.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding function: {e}")
            raise
    
    def get_embedding_function(self):
        """
        Получить функцию для создания эмбеддингов
        
        Returns:
            Функция для создания эмбеддингов
        """
        return self.embedding_function
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Создает эмбеддинги для списка текстов
        
        Args:
            texts: Список текстов для эмбеддинга
            
        Returns:
            Массив эмбеддингов размерности (n_texts, embedding_dim)
        """
        try:
            embeddings = self.embedding_function(texts)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        L2-нормализует эмбеддинги по каждой строке
        
        Args:
            embeddings: Массив эмбеддингов
            
        Returns:
            Нормализованные эмбеддинги
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / np.where(norms == 0, 1, norms)
    
    def compute_cosine_similarity(self, 
                                 query_embeddings: np.ndarray, 
                                 document_embeddings: np.ndarray) -> np.ndarray:
        """
        Вычисляет косинусное сходство между запросами и документами
        
        Args:
            query_embeddings: Эмбеддинги запросов, размерности (n_queries, embedding_dim)
            document_embeddings: Эмбеддинги документов, размерности (n_docs, embedding_dim)
            
        Returns:
            Матрица косинусного сходства размерности (n_queries, n_docs)
        """
        # Нормализуем эмбеддинги для косинусного сходства
        query_norm = self.normalize_embeddings(query_embeddings)
        doc_norm = self.normalize_embeddings(document_embeddings)
        
        # Вычисляем косинусное сходство как скалярное произведение нормализованных векторов
        return query_norm.dot(doc_norm.T)
    
    def process_excel_data(self, file_name: str, sheet_name: str) -> Dict[str, Any]:
        """
        Обработка Excel-файла и подготовка данных для эмбеддингов
        
        Args:
            file_name: Путь к Excel-файлу
            sheet_name: Имя листа в Excel-файле
            
        Returns:
            Словарь со структурированными данными для сохранения в ChromaDB
        """
        logger.info(f"Processing Excel data from file: {file_name}, sheet: {sheet_name}")
        
        try:
            # Чтение данных из Excel
            spec_data = pd.read_excel(file_name, sheet_name=sheet_name, header=[0,1,2,3])
            spec_data = spec_data.fillna("")
            logger.info(f"Successfully read Excel data with shape: {spec_data.shape}")
            
            # Обработка данных
            res = {}
            res['description_full'] = []
            
            # Обрабатываем заголовки столбцов
            for i in spec_data.columns:
                ii = list(i)
                res['description_full'].append({})
                res['description_full'][-1]['column_title'] = ''
                
                for j in range(1, len(ii)):
                    if not (ii[j].startswith("Unnamed")):
                        res['description_full'][-1]['column_title'] += ii[j]
                        res['description_full'][-1]['column_title'] += '__'
                
                res['description_full'][-1]['column_title'] = res['description_full'][-1]['column_title'][:-2]
                res['description_full'][-1]['column_text'] = " ".join(spec_data[i].tolist()).strip()
            
            # Готовим данные для ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for j in range(len(res['description_full'])):
                ids.append(f"id{j}")
                documents.append(res['description_full'][j]['column_text'])
                md = {
                    'column_title': res['description_full'][j]['column_title']
                }
                metadatas.append(deepcopy(md))
            
            # Создаем метаданные коллекции
            collection_metadata = {
                "source_file": file_name,
                "sheet_name": sheet_name,
                "conf_title": spec_data.columns[0][0],
                "conf_title_short": sheet_name
            }
            
            logger.info(f"Processed {len(documents)} documents from Excel data")
            
            return {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
                "collection_metadata": collection_metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel data: {e}")
            raise 
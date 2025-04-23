import chromadb
from typing import List, Dict, Any, Optional
from loguru import logger
from ..utils.config_loader import ConfigLoader
from ..embedder import EmbeddingProcessor

class ChromaDBManager:
    """
    Класс для управления коллекциями в ChromaDB
    """
    def __init__(self, embedding_processor=None):
        """
        Инициализация менеджера ChromaDB и установление соединения
        
        Args:
            embedding_processor: Процессор эмбеддингов (опционально)
                              Если не указан, будет создан новый
        """
        config_loader = ConfigLoader()
        config = config_loader.load_config()
        self.host = config_loader.get_host()
        self.port = config_loader.get_port()
        
        logger.info(f"Initializing ChromaDBManager with host: {self.host}, port: {self.port}")
        
        # Устанавливаем соединение с ChromaDB
        try:
            self.chroma_client = chromadb.HttpClient(host=self.host, port=self.port)
            logger.info("Successfully connected to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
        
        # Используем переданный процессор эмбеддингов или создаем новый
        if embedding_processor:
            self.embedding_processor = embedding_processor
            self.embedding_function = embedding_processor.get_embedding_function()
        else:
            try:
                self.embedding_processor = EmbeddingProcessor()
                self.embedding_function = self.embedding_processor.get_embedding_function()
                logger.info(f"Created new embedding processor")
            except Exception as e:
                logger.error(f"Failed to create embedding processor: {e}")
                raise
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        Получить список всех коллекций в ChromaDB
        
        Returns:
            Список коллекций с их метаданными
        """
        try:
            collections = self.chroma_client.list_collections()
            logger.info(f"Listed {len(collections)} collections in ChromaDB")
            return collections
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Создать новую коллекцию
        
        Args:
            name: Имя коллекции
            metadata: Метаданные коллекции (опционально)
            
        Returns:
            Объект коллекции
        """
        try:
            # Пробуем получить существующую коллекцию
            collection = self.chroma_client.get_collection(
                name=name, 
                embedding_function=self.embedding_function
            )
            logger.info(f"Collection '{name}' already exists.")
        except Exception:
            # Если коллекция не существует, создаем новую
            collection = self.chroma_client.create_collection(
                name=name,
                metadata=metadata,
                embedding_function=self.embedding_function
            )
            logger.info(f"Created new collection '{name}' with metadata: {metadata}")
        
        return collection
    
    def get_collection(self, name: str) -> Any:
        """
        Получить коллекцию по имени
        
        Args:
            name: Имя коллекции
            
        Returns:
            Объект коллекции или None, если коллекция не найдена
        """
        try:
            collection = self.chroma_client.get_collection(
                name=name, 
                embedding_function=self.embedding_function
            )
            logger.info(f"Retrieved collection '{name}'")
            return collection
        except Exception as e:
            logger.error(f"Error getting collection '{name}': {e}")
            return None
    
    def add_documents(self, 
                     collection_name: str, 
                     documents: List[str], 
                     metadatas: Optional[List[Dict[str, Any]]] = None, 
                     ids: Optional[List[str]] = None) -> bool:
        """
        Добавить документы в коллекцию
        
        Args:
            collection_name: Имя коллекции
            documents: Список текстов документов
            metadatas: Список метаданных для каждого документа (опционально)
            ids: Список идентификаторов для каждого документа (опционально)
            
        Returns:
            True, если документы успешно добавлены, иначе False
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return False
            
            # Генерируем идентификаторы, если они не предоставлены
            if not ids:
                ids = [f"id{i}" for i in range(len(documents))]
            
            # Добавляем документы в коллекцию
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to collection '{collection_name}': {e}")
            return False
    
    def get_collection_contents(self, 
                              collection_name: str, 
                              include: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Получить все содержимое коллекции
        
        Args:
            collection_name: Имя коллекции
            include: Что включать в результаты ("documents", "metadatas", "embeddings")
            
        Returns:
            Содержимое коллекции или пустой словарь в случае ошибки
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return {}
            
            # Устанавливаем, что включать в результаты по умолчанию
            if include is None:
                include = ["documents", "metadatas"]
            
            # Получаем все содержимое коллекции
            contents = collection.get(include=include)
            
            logger.info(f"Got contents for collection '{collection_name}': {len(contents.get('ids', []))} documents")
            return contents
        except Exception as e:
            logger.error(f"Error getting collection contents for '{collection_name}': {e}")
            return {}
    
    def add_from_excel(self, file_name: str, sheet_name: str, collection_name: str) -> bool:
        """
        Добавить данные из Excel-файла в коллекцию ChromaDB
        
        Args:
            file_name: Путь к Excel-файлу
            sheet_name: Имя листа в Excel-файле
            collection_name: Имя коллекции для создания/обновления
            
        Returns:
            True, если данные успешно добавлены, иначе False
        """
        try:
            # Используем текущий процессор эмбеддингов
            processor = self.embedding_processor
            
            # Обрабатываем данные из Excel
            data = processor.process_excel_data(file_name, sheet_name)
            
            # Создаем или получаем коллекцию
            self.create_collection(
                name=collection_name, 
                metadata=data["collection_metadata"]
            )
            
            # Добавляем документы в коллекцию
            success = self.add_documents(
                collection_name=collection_name,
                documents=data["documents"],
                metadatas=data["metadatas"],
                ids=data["ids"]
            )
            
            if success:
                logger.info(f"Successfully added data from {file_name} ({sheet_name}) to collection '{collection_name}'")
            else:
                logger.error(f"Failed to add data from {file_name} to collection '{collection_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error adding data from Excel to collection: {e}")
            return False
    
    def delete_all_collections(self) -> Dict[str, Any]:
        """
        Удалить все коллекции в ChromaDB
        
        Returns:
            Словарь с информацией о результатах удаления:
            {
                "success": bool - общий успех операции,
                "total": int - общее количество коллекций,
                "deleted": int - количество успешно удаленных коллекций,
                "failed": int - количество коллекций, которые не удалось удалить,
                "failed_collections": List[str] - имена коллекций, которые не удалось удалить
            }
        """
        try:
            # Получаем список всех коллекций
            collections = self.list_collections()
            
            if not collections:
                logger.info("No collections found to delete")
                return {
                    "success": True,
                    "total": 0,
                    "deleted": 0,
                    "failed": 0,
                    "failed_collections": []
                }
            
            # Счетчики для отслеживания прогресса
            deleted_count = 0
            failed_count = 0
            failed_collections = []
            
            # Удаляем каждую коллекцию
            for collection in collections:
                collection_name = collection.name
                try:
                    self.chroma_client.delete_collection(name=collection_name)
                    deleted_count += 1
                    logger.info(f"Deleted collection '{collection_name}'")
                except Exception as e:
                    failed_count += 1
                    failed_collections.append(collection_name)
                    logger.error(f"Failed to delete collection '{collection_name}': {e}")
            
            # Определяем общий успех операции
            success = failed_count == 0
            
            # Результат операции
            result = {
                "success": success,
                "total": len(collections),
                "deleted": deleted_count,
                "failed": failed_count,
                "failed_collections": failed_collections
            }
            
            logger.info(f"Delete all collections operation completed: {deleted_count} deleted, {failed_count} failed")
            return result
            
        except Exception as e:
            logger.error(f"Error in delete_all_collections: {e}")
            return {
                "success": False,
                "total": 0,
                "deleted": 0,
                "failed": 0,
                "failed_collections": [],
                "error": str(e)
            } 
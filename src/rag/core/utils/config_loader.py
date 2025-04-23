import os
import yaml
from loguru import logger
from typing import Dict, Any


class ConfigLoader:
    """
    Класс для загрузки конфигурации из YAML файлов.
    Реализует паттерн Синглтон, чтобы гарантировать единственный экземпляр и загрузку конфигурации один раз.
    """
    _instance = None
    _config_loaded = False
    
    def __new__(cls, config_path: str = None):
        """
        Реализация паттерна Синглтон.
        Возвращает существующий экземпляр класса или создает новый.
        """
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance.config_path = config_path
            cls._instance.config_data = None
        elif config_path is not None and cls._instance.config_path != config_path:
            logger.warning(f"ConfigLoader уже инициализирован с путем {cls._instance.config_path}, " 
                           f"игнорирование нового пути {config_path}")
        return cls._instance
    
    def __init__(self, config_path: str = None):
        """
        Инициализация загрузчика конфигурации.
        Если экземпляр уже существует, просто обновляет путь если он отличается.
        
        Args:
            config_path: Путь к конфигурационному YAML файлу. Если None, используется путь по умолчанию.
        """
        # Если __new__ вернул существующий экземпляр, этот код не будет изменять config_path,
        # поэтому нам нужно проверить только случай, когда path не установлен
        if self.config_path is None:
            if config_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.config_path = os.path.join(current_dir, '../../config/config.yaml')
            else:
                self.config_path = config_path
    
    def load_config(self) -> Dict[str, Any]:
        """
        Загрузка конфигурации из YAML файла.
        Загружает только один раз, повторные вызовы возвращают кэшированные данные.
        
        Returns:
            Словарь с конфигурационными значениями
        """
        # Если конфигурация уже загружена, возвращаем кэшированные данные
        if ConfigLoader._config_loaded and self.config_data is not None:
            return self.config_data
        
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Конфигурационный файл не найден: {self.config_path}")
                raise FileNotFoundError(f"Конфигурационный файл не найден: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as config_file:
                self.config_data = yaml.safe_load(config_file)
                
            if not self.config_data:
                logger.warning("Конфигурационный файл пуст или недействителен")
                raise ValueError("Конфигурационный файл пуст или недействителен")
                
            logger.info(f"Конфигурация успешно загружена: {self.config_data}")
            ConfigLoader._config_loaded = True
            return self.config_data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            raise
    
    def get_value(self, key: str) -> Any:
        """
        Получение конкретного значения конфигурации по ключу.
        
        Args:
            key: Ключ конфигурации для получения
            
        Returns:
            Значение конфигурации
            
        Raises:
            KeyError: Если ключ не найден в конфигурации
        """
        if self.config_data is None:
            self.load_config()
            
        if key not in self.config_data:
            logger.error(f"Ключ '{key}' не найден в конфигурации")
            raise KeyError(f"Ключ '{key}' не найден в конфигурации")
        
        return self.config_data[key]
    
    def get_rag_prompt(self) -> str:
        """
        Получение промта RAG из конфигурации.
        
        Returns:
            Промт RAG
        """
        return self.get_value('rag_promt')
    
    def get_general_top(self) -> int:
        """
        Получение количества результатов для общего поиска.
        
        Returns:
            Количество результатов для общего поиска
        """
        return int(self.get_value('general_top'))
    
    def get_article_top(self) -> int:
        """
        Получение количества результатов для поиска по статье.
        
        Returns:
            Количество результатов для поиска по статье
        """
        return int(self.get_value('artical_top'))
    
    def get_host(self) -> str:
        """
        Получение значения хоста из конфигурации.
        
        Returns:
            Хост в виде строки
        """
        return self.get_value('host')
    
    def get_port(self) -> int:
        """
        Получение значения порта из конфигурации.
        
        Returns:
            Порт в виде целого числа
        """
        return int(self.get_value('port'))
    
    def get_embedding_model(self) -> str:
        """
        Получение модели эмбеддингов из конфигурации.
        
        Returns:
            Название модели эмбеддингов
        """
        return self.get_value('embedding_model')

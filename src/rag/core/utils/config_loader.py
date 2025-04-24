import os
import yaml
from loguru import logger
from typing import Dict, Any


class ConfigLoader:
    """
    Class for loading configuration from YAML files
    :param self: Instance of ConfigLoader
    :return: None
    """
    _instance = None
    _config_loaded = False
    
    def __new__(cls, config_path: str = None):
        """
        Implementation of the Singleton pattern
        :param cls: Class of ConfigLoader
        :param config_path: Path to the YAML configuration file
        :return: Instance of ConfigLoader
        """
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance.config_path = config_path
            cls._instance.config_data = None
        elif config_path is not None and cls._instance.config_path != config_path:
            logger.warning(f"ConfigLoader already initialized with path {cls._instance.config_path}, " 
                           f"ignoring new path {config_path}")
        return cls._instance
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration loader
        :param self: Instance of ConfigLoader
        :param config_path: Path to the YAML configuration file
        :return: None
        """
        # If __new__ returned an existing instance, this code won't change config_path,
        # so we only need to check the case when path is not set
        if self.config_path is None:
            if config_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.config_path = os.path.join(current_dir, '../../config/config.yaml')
            else:
                self.config_path = config_path
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        :param self: Instance of ConfigLoader
        :return: Dictionary with configuration values
        """
        # If configuration is already loaded, return cached data
        if ConfigLoader._config_loaded and self.config_data is not None:
            return self.config_data
        
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Configuration file not found: {self.config_path}")
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as config_file:
                self.config_data = yaml.safe_load(config_file)
                
            if not self.config_data:
                logger.warning("Configuration file is empty or invalid")
                raise ValueError("Configuration file is empty or invalid")
                
            logger.info(f"Configuration successfully loaded: {self.config_data}")
            ConfigLoader._config_loaded = True
            return self.config_data
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def get_value(self, key: str) -> Any:
        """
        Get a specific configuration value by key
        :param self: Instance of ConfigLoader
        :param key: Configuration key to retrieve
        :return: Configuration value
        """
        if self.config_data is None:
            self.load_config()
            
        if key not in self.config_data:
            logger.error(f"Key '{key}' not found in configuration")
            raise KeyError(f"Key '{key}' not found in configuration")
        
        return self.config_data[key]
    
    def get_rag_prompt(self) -> str:
        """
        Get the RAG prompt from the configuration
        :param self: Instance of ConfigLoader
        :return: RAG prompt
        """
        return self.get_value('rag_promt')
    
    def get_general_top(self) -> int:
        """
        Get the number of results for general search
        :param self: Instance of ConfigLoader
        :return: Number of results for general search
        """
        return int(self.get_value('general_top'))
    
    def get_article_top(self) -> int:
        """
        Get the number of results for article search
        :param self: Instance of ConfigLoader
        :return: Number of results for article search
        """
        return int(self.get_value('artical_top'))
    
    def get_host(self) -> str:
        """
        Get the host value from the configuration
        :param self: Instance of ConfigLoader
        :return: Host as a string
        """
        return self.get_value('host')
    
    def get_port(self) -> int:
        """
        Get the port value from the configuration
        :param self: Instance of ConfigLoader
        :return: Port as an integer
        """
        return int(self.get_value('port'))
    
    def get_embedding_model(self) -> str:
        """
        Get the embedding model from the configuration
        :param self: Instance of ConfigLoader
        :return: Embedding model name
        """
        return self.get_value('embedding_model')
    
    def get_additional_info_prefix(self) -> str:
        """
        Get the additional information prefix from the configuration
        :param self: Instance of ConfigLoader
        :return: Additional information prefix
        """
        return self.get_value('additional_info_prefix')

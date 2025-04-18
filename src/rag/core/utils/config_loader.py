import os
import yaml
from loguru import logger
from typing import Dict, Any, Optional


class ConfigLoader:
    """
    Utility class for loading configuration from YAML files.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the YAML config file. If None, uses default path.
        """
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(current_dir, '../../config/config.yaml')
        else:
            self.config_path = config_path
            
        self.config_data = None
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the YAML file.
        
        Returns:
            Dictionary containing configuration values
        """
        try:
            
            if not os.path.exists(self.config_path):
                logger.error(f"Config file not found: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r') as config_file:
                self.config_data = yaml.safe_load(config_file)
                
            if not self.config_data:
                logger.warning("Config file is empty or invalid")
                self.config_data = {}
                
            logger.info(f"Configuration loaded successfully: {self.config_data}")
            return self.config_data
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value by key.
        
        Args:
            key: Configuration key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default
        """
        if self.config_data is None:
            self.load_config()
            
        value = self.config_data.get(key, default)
        return value
    
    def get_text_processor_config(self) -> Dict[str, Any]:
        """
        Get configuration specifically for the text processor.
        
        Returns:
            Dictionary with text processor configuration
        """
        if self.config_data is None:
            self.load_config()
            
        # Get text processor specific configuration
        count_keywords = self.get_value('count_keywords', 10)
        
        config = {
            'max_keywords': count_keywords
        }
        
        return config

    def get_host(self) -> str:
        """
        Get the host value from the configuration.

        Returns:
            Host as a string
        """
        return self.get_value('host')

    def get_port(self) -> int:
        """
        Get the port value from the configuration.

        Returns:
            Port as an integer
        """
        return int(self.get_value('port'))

    def get_collections_file(self) -> str:
        """
        Get the collections file value from the configuration.

        Returns:
            Collections file as a string
        """
        return self.get_value('collections_file')

    def get_embedding_model(self) -> str:
        """
        Get the embedding model value from the configuration.

        Returns:
            Embedding model as a string
        """
        return self.get_value('embedding_model')

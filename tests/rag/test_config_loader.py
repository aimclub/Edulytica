import unittest
import os
import yaml
from unittest.mock import patch, mock_open, MagicMock

from src.rag.core.utils.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """Tests for ConfigLoader class"""

    def setUp(self):
        """Set up the test environment"""
        # Reset ConfigLoader singleton between tests
        ConfigLoader._instance = None
        ConfigLoader._config_loaded = False
        
        # Sample config data for testing
        self.sample_config = {
            'host': 'localhost',
            'port': 8000,
            'embedding_model': 'all-MiniLM-L6-v2',
            'rag_promt': 'This is a RAG prompt template',
            'general_top': 5,
            'artical_top': 2,
            'additional_info_prefix': 'Additional info: '
        }
        
        # Используем более точное патчирование вместо патчирования всего модуля yaml
        # Создаем патч для yaml.safe_load
        self.yaml_safe_load_patcher = patch('src.rag.core.utils.config_loader.yaml.safe_load')
        self.mock_yaml_load = self.yaml_safe_load_patcher.start()
        self.mock_yaml_load.return_value = self.sample_config
        
        # Создаем патч для os.path.exists
        self.os_path_exists_patcher = patch('src.rag.core.utils.config_loader.os.path.exists')
        self.mock_os_path_exists = self.os_path_exists_patcher.start()
        self.mock_os_path_exists.return_value = True
        
        # Создаем патч для open
        self.open_patcher = patch('src.rag.core.utils.config_loader.open', 
                                  new_callable=mock_open, 
                                  read_data='dummy_yaml_content')
        self.mock_open = self.open_patcher.start()

    def tearDown(self):
        """Clean up after each test"""
        self.yaml_safe_load_patcher.stop()
        self.os_path_exists_patcher.stop()
        self.open_patcher.stop()

    def test_singleton_pattern(self):
        """Test that ConfigLoader implements the Singleton pattern"""
        # Create two instances
        config_loader1 = ConfigLoader()
        config_loader2 = ConfigLoader()
        
        # Check that they are the same instance
        self.assertIs(config_loader1, config_loader2)
        
        # Check that warning is logged when different path is provided
        with patch('src.rag.core.utils.config_loader.logger.warning') as mock_logger:
            config_loader3 = ConfigLoader("different/path.yaml")
            mock_logger.assert_called_once()
            
        # Check that it's still the same instance
        self.assertIs(config_loader1, config_loader3)

    def test_init_with_default_path(self):
        """Test initialization with default path"""
        config_loader = ConfigLoader()
        
        # Check that the path ends with the expected default path
        self.assertTrue(config_loader.config_path.endswith('src/rag/config/config.yaml'))

    def test_init_with_custom_path(self):
        """Test initialization with custom path"""
        custom_path = "/path/to/custom/config.yaml"
        config_loader = ConfigLoader(custom_path)
        
        # Check that the path is set correctly
        self.assertEqual(config_loader.config_path, custom_path)

    def test_load_config(self):
        """Test loading configuration from file"""
        config_loader = ConfigLoader()
        result = config_loader.load_config()
        
        # Check that the file was opened with the correct path
        self.mock_open.assert_called_once()
        
        # Check that yaml.safe_load was called with the file
        self.mock_yaml_load.assert_called_once()
        
        # Check that the result is the sample config
        self.assertEqual(result, self.sample_config)
        
        # Check that the config is cached
        self.assertTrue(ConfigLoader._config_loaded)
        self.assertEqual(config_loader.config_data, self.sample_config)

    def test_load_config_file_not_found(self):
        """Test handling when config file is not found"""
        # Configure mock to return False (file doesn't exist)
        self.mock_os_path_exists.return_value = False
        
        config_loader = ConfigLoader()
        
        # Check that FileNotFoundError is raised
        with self.assertRaises(FileNotFoundError):
            config_loader.load_config()

    def test_load_config_empty_file(self):
        """Test handling when config file is empty"""
        # Configure mock to return None (empty file)
        self.mock_yaml_load.return_value = None
        
        config_loader = ConfigLoader()
        
        # Check that ValueError is raised
        with self.assertRaises(ValueError):
            config_loader.load_config()

    def test_load_config_cached(self):
        """Test that configuration is cached after first load"""
        config_loader = ConfigLoader()
        
        # Load config first time
        result1 = config_loader.load_config()
        
        # Reset mocks to check if they are called again
        self.mock_open.reset_mock()
        self.mock_yaml_load.reset_mock()
        
        # Load config second time
        result2 = config_loader.load_config()
        
        # Check that the file wasn't opened again
        self.mock_open.assert_not_called()
        
        # Check that yaml.safe_load wasn't called again
        self.mock_yaml_load.assert_not_called()
        
        # Check that both results are the same
        self.assertEqual(result1, result2)

    def test_get_value(self):
        """Test getting a specific value from the configuration"""
        config_loader = ConfigLoader()
        
        # Вместо прямого изменения config_data, создаем патч для load_config
        with patch.object(config_loader, 'load_config', return_value=self.sample_config):
            # Устанавливаем данные напрямую, чтобы избежать вызова load_config
            config_loader.config_data = self.sample_config
            
            # Test getting a value
            result = config_loader.get_value('host')
            
            # Check the result
            self.assertEqual(result, 'localhost')

    def test_get_value_key_error(self):
        """Test getting a non-existent value from the configuration"""
        config_loader = ConfigLoader()
        
        # Устанавливаем данные напрямую, чтобы избежать вызова load_config
        config_loader.config_data = self.sample_config
        
        # Check that KeyError is raised for non-existent key
        with self.assertRaises(KeyError):
            config_loader.get_value('non_existent_key')

    def test_get_value_loads_config(self):
        """Test that get_value loads the config if not already loaded"""
        config_loader = ConfigLoader()
        
        # Используем patch.object вместо прямого изменения config_data
        with patch.object(ConfigLoader, 'load_config', return_value=self.sample_config):
            # Reset config_data to None
            config_loader.config_data = None
            
            # Call get_value
            result = config_loader.get_value('host')
            
            # Проверяем, что load_config был вызван
            ConfigLoader.load_config.assert_called_once()
            
            # Check the result
            self.assertEqual(result, 'localhost')

    def test_get_rag_prompt(self):
        """Test getting the RAG prompt"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value вместо прямого изменения config_data
        with patch.object(config_loader, 'get_value', return_value='This is a RAG prompt template'):
            # Test getting the RAG prompt
            result = config_loader.get_rag_prompt()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('rag_promt')
            
            # Check the result
            self.assertEqual(result, 'This is a RAG prompt template')

    def test_get_general_top(self):
        """Test getting the general top value"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value
        with patch.object(config_loader, 'get_value', return_value=5):
            # Test getting the general top value
            result = config_loader.get_general_top()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('general_top')
            
            # Check the result is an integer
            self.assertIsInstance(result, int)
            self.assertEqual(result, 5)

    def test_get_article_top(self):
        """Test getting the article top value"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value
        with patch.object(config_loader, 'get_value', return_value=2):
            # Test getting the article top value
            result = config_loader.get_article_top()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('artical_top')
            
            # Check the result is an integer
            self.assertIsInstance(result, int)
            self.assertEqual(result, 2)

    def test_get_host(self):
        """Test getting the host value"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value
        with patch.object(config_loader, 'get_value', return_value='localhost'):
            # Test getting the host value
            result = config_loader.get_host()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('host')
            
            # Check the result
            self.assertEqual(result, 'localhost')

    def test_get_port(self):
        """Test getting the port value"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value
        with patch.object(config_loader, 'get_value', return_value=8000):
            # Test getting the port value
            result = config_loader.get_port()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('port')
            
            # Check the result is an integer
            self.assertIsInstance(result, int)
            self.assertEqual(result, 8000)

    def test_get_embedding_model(self):
        """Test getting the embedding model"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value
        with patch.object(config_loader, 'get_value', return_value='all-MiniLM-L6-v2'):
            # Test getting the embedding model
            result = config_loader.get_embedding_model()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('embedding_model')
            
            # Check the result
            self.assertEqual(result, 'all-MiniLM-L6-v2')

    def test_get_additional_info_prefix(self):
        """Test getting the additional info prefix"""
        config_loader = ConfigLoader()
        
        # Используем patch.object для метода get_value
        with patch.object(config_loader, 'get_value', return_value='Additional info: '):
            # Test getting the additional info prefix
            result = config_loader.get_additional_info_prefix()
            
            # Проверяем, что get_value был вызван с правильным параметром
            config_loader.get_value.assert_called_once_with('additional_info_prefix')
            
            # Check the result
            self.assertEqual(result, 'Additional info: ')


if __name__ == '__main__':
    unittest.main() 
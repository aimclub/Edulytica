import unittest
import os
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open

from src.rag.core.embedder.embedding_processor import EmbeddingProcessor


class TestEmbeddingProcessor(unittest.TestCase):
    """Tests for EmbeddingProcessor class"""

    def setUp(self):
        """Set up the test environment with mocks for all dependencies"""
        # Создаем моки сначала, до патчинга
        # Подготавливаем мок для конфигурации
        self.mock_config_instance = MagicMock()
        self.mock_config_instance.get_embedding_model.return_value = "all-MiniLM-L6-v2"
        
        # Подготавливаем мок для embedding функции
        self.mock_embedding_function = MagicMock()
        self.mock_embedding_function.side_effect = lambda texts: [[0.1, 0.2, 0.3] for _ in texts]
        
        # Подготавливаем мок для chromadb
        self.mock_embedding_functions = MagicMock()
        self.mock_embedding_functions.SentenceTransformerEmbeddingFunction.return_value = self.mock_embedding_function
        
        # Патчим зависимости
        self.config_loader_patcher = patch('src.rag.core.utils.config_loader.ConfigLoader')
        self.chromadb_utils_patcher = patch('src.rag.core.embedder.embedding_processor.chromadb.utils.embedding_functions')
        self.pandas_read_excel_patcher = patch('src.rag.core.embedder.embedding_processor.pd.read_excel')
        
        # Запускаем патчи
        self.mock_config_loader_class = self.config_loader_patcher.start()
        self.mock_chromadb_utils = self.chromadb_utils_patcher.start()
        self.mock_pandas_read_excel = self.pandas_read_excel_patcher.start()
        
        # Настраиваем возвращаемые значения
        self.mock_config_loader_class.return_value = self.mock_config_instance
        self.mock_chromadb_utils.SentenceTransformerEmbeddingFunction.return_value = self.mock_embedding_function

        # Создаем экземпляр EmbeddingProcessor
        self.embedding_processor = EmbeddingProcessor()

    def tearDown(self):
        """Stop all patches"""
        self.config_loader_patcher.stop()
        self.chromadb_utils_patcher.stop()
        self.pandas_read_excel_patcher.stop()

    def test_init(self):
        """Test initialization of EmbeddingProcessor class"""
        # Check that the config loader was used to get the model
        self.mock_config_instance.get_embedding_model.assert_called_once()
        
        # Check that the embedding function was created with the right model
        self.mock_chromadb_utils.SentenceTransformerEmbeddingFunction.assert_called_once_with(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Check that the model name was stored
        self.assertEqual(self.embedding_processor.embedding_model, "all-MiniLM-L6-v2")

    def test_init_with_custom_model(self):
        """Test initialization with custom model"""
        # Сбрасываем счетчики вызовов
        self.mock_chromadb_utils.SentenceTransformerEmbeddingFunction.reset_mock()
        
        custom_processor = EmbeddingProcessor(embedding_model="custom-model")
        
        # Check that the embedding function was created with the custom model
        self.mock_chromadb_utils.SentenceTransformerEmbeddingFunction.assert_called_once_with(
            model_name="custom-model"
        )
        
        # Check that the model name was stored
        self.assertEqual(custom_processor.embedding_model, "custom-model")

    def test_get_embedding_function(self):
        """Test getting the embedding function"""
        # Get the embedding function
        result = self.embedding_processor.get_embedding_function()
        
        # Check that the correct function was returned
        self.assertEqual(result, self.mock_embedding_function)

    def test_embed_texts(self):
        """Test creating embeddings for texts"""
        # Выполняем метод встраивания текстов
        texts = ["text1", "text2", "text3"]
        
        # Используем патч метода для избежания ошибок super()
        with patch.object(self.embedding_processor, 'embedding_function', self.mock_embedding_function):
            result = self.embedding_processor.embed_texts(texts)
        
            # Check the embedding function was called with the correct parameters
            self.mock_embedding_function.assert_called_once_with(texts)
            
            # Check the result is a numpy array with the correct shape
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, (3, 3))  # 3 texts with 3 dimensions each
            np.testing.assert_array_almost_equal(result, np.array([[0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]))

    def test_normalize_embeddings(self):
        """Test normalizing embeddings"""
        # Create sample embeddings
        embeddings = np.array([
            [1.0, 2.0, 2.0],  # norm = 3
            [3.0, 0.0, 4.0]   # norm = 5
        ])
        
        # Test the method
        result = self.embedding_processor.normalize_embeddings(embeddings)
        
        # Check the result is normalized (unit vectors)
        expected = np.array([
            [1/3, 2/3, 2/3],  # normalized
            [3/5, 0, 4/5]     # normalized
        ])
        np.testing.assert_array_almost_equal(result, expected)
        
        # Check that all vectors have unit norm
        norms = np.linalg.norm(result, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(2))

    def test_normalize_embeddings_with_zero_vector(self):
        """Test normalizing embeddings with a zero vector"""
        # Create sample embeddings with a zero vector
        embeddings = np.array([
            [1.0, 2.0, 2.0],  # norm = 3
            [0.0, 0.0, 0.0]   # norm = 0
        ])
        
        # Test the method
        result = self.embedding_processor.normalize_embeddings(embeddings)
        
        # Check the result handles zero vectors correctly
        expected = np.array([
            [1/3, 2/3, 2/3],  # normalized
            [0, 0, 0]         # zero vector remains zero
        ])
        np.testing.assert_array_almost_equal(result, expected)

    def test_compute_cosine_similarity(self):
        """Test computing cosine similarity"""
        # Create sample embeddings
        query_embeddings = np.array([
            [1.0, 0.0, 0.0],  # query 1
            [0.0, 1.0, 0.0]   # query 2
        ])
        
        document_embeddings = np.array([
            [1.0, 0.0, 0.0],  # doc 1 - identical to query 1
            [0.0, 0.0, 1.0],  # doc 2 - orthogonal to all queries
            [0.0, 1.0, 0.0]   # doc 3 - identical to query 2
        ])
        
        # Используем патч метода normalize_embeddings вместо прямого изменения
        with patch.object(self.embedding_processor, 'normalize_embeddings', side_effect=lambda x: x):
            # Test the method
            result = self.embedding_processor.compute_cosine_similarity(query_embeddings, document_embeddings)
            
            # Проверяем, что метод normalize_embeddings был вызван дважды
            self.assertEqual(self.embedding_processor.normalize_embeddings.call_count, 2)
            
            # Check the result is a similarity matrix with correct values
            expected = np.array([
                [1.0, 0.0, 0.0],  # query 1 similar to doc 1, not to others
                [0.0, 0.0, 1.0]   # query 2 similar to doc 3, not to others
            ])
            np.testing.assert_array_almost_equal(result, expected)

    def test_process_excel_data(self):
        """Test processing Excel data"""
        # Create a mock DataFrame with multi-level columns
        mock_df = pd.DataFrame()
        mock_df.columns = pd.MultiIndex.from_tuples([
            ('Conference', 'Name', 'Type', 'Unnamed'),
            ('Date', 'Start', 'Unnamed', 'Unnamed'),
            ('Session', 'Title', 'Description', 'Unnamed')
        ])
        
        # Add some data
        mock_df['Conference'] = ["Conference A", "Conference B"]
        mock_df['Date'] = ["2023-01-01", "2023-01-02"]
        mock_df['Session'] = ["Session X", "Session Y"]
        
        # Configure the mock to return our DataFrame
        self.mock_pandas_read_excel.return_value = mock_df
        
        # Test the method
        result = self.embedding_processor.process_excel_data("fake_file.xlsx", "Sheet1")
        
        # Check the read_excel was called with correct parameters
        self.mock_pandas_read_excel.assert_called_once_with("fake_file.xlsx", sheet_name="Sheet1", header=[0, 1, 2, 3])
        
        # Check the result has the expected structure
        self.assertIn("ids", result)
        self.assertIn("documents", result)
        self.assertIn("metadatas", result)
        self.assertIn("collection_metadata", result)
        
        # Check the number of documents matches expected columns
        self.assertEqual(len(result["documents"]), 3)  # 3 columns
        
        # Check collection metadata
        self.assertEqual(result["collection_metadata"]["source_file"], "fake_file.xlsx")
        self.assertEqual(result["collection_metadata"]["sheet_name"], "Sheet1")

    def test_process_excel_data_error(self):
        """Test handling of errors in Excel processing"""
        # Configure the mock to raise an exception
        self.mock_pandas_read_excel.side_effect = Exception("File not found")
        
        # Test that the method raises the exception
        with self.assertRaises(Exception):
            self.embedding_processor.process_excel_data("non_existent_file.xlsx", "Sheet1")


if __name__ == '__main__':
    unittest.main() 
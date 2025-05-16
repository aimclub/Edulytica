import unittest
import os
from unittest.mock import patch, MagicMock

from src.rag.core.chroma_db.chroma_manager import ChromaDBManager


class TestChromaDBManager(unittest.TestCase):
    """Tests for ChromaDBManager class"""

    def setUp(self):
        """Set up the test environment with mocks for all dependencies"""
        # Подготавливаем моки для конфигурации
        self.mock_config_instance = MagicMock()
        self.mock_config_instance.load_config.return_value = {"chromadb": {"host": "localhost", "port": 8000}}
        self.mock_config_instance.get_host.return_value = "localhost"
        self.mock_config_instance.get_port.return_value = 8000
        
        # Подготавливаем моки для embedding processor
        self.mock_embedding_processor = MagicMock()
        self.mock_embedding_function = MagicMock()
        self.mock_embedding_processor.get_embedding_function.return_value = self.mock_embedding_function
        
        # Подготавливаем моки для ChromaDB
        self.mock_chroma_client = MagicMock()
        
        # Патчим только конкретные функции, не затрагивая классы целиком
        self.config_loader_patcher = patch('src.rag.core.utils.config_loader.ConfigLoader')
        self.embedding_processor_patcher = patch('src.rag.core.chroma_db.chroma_manager.EmbeddingProcessor')
        self.chromadb_patcher = patch('src.rag.core.chroma_db.chroma_manager.chromadb')

        # Запускаем патчи
        self.mock_config_loader_class = self.config_loader_patcher.start()
        self.mock_embedding_processor_class = self.embedding_processor_patcher.start()
        self.mock_chromadb = self.chromadb_patcher.start()

        # Настраиваем возвращаемые значения
        self.mock_config_loader_class.return_value = self.mock_config_instance
        self.mock_embedding_processor_class.return_value = self.mock_embedding_processor
        self.mock_chromadb.HttpClient.return_value = self.mock_chroma_client

        # Создаем экземпляр ChromaDBManager
        self.chroma_manager = ChromaDBManager()

    def tearDown(self):
        """Stop all patches"""
        self.config_loader_patcher.stop()
        self.embedding_processor_patcher.stop()
        self.chromadb_patcher.stop()

    def test_init(self):
        """Test initialization of ChromaDBManager class"""
        # Check that ChromaDB client is created with correct parameters
        self.mock_chromadb.HttpClient.assert_called_once_with(host="localhost", port=8000)
        
        # Check that embedding processor is created
        self.mock_embedding_processor_class.assert_called_once()
        
        # Check that embedding function is retrieved
        self.assertEqual(self.chroma_manager.embedding_function, self.mock_embedding_function)

    def test_init_with_embedding_processor(self):
        """Test initialization with provided embedding processor"""
        custom_embedding_processor = MagicMock()
        custom_embedding_function = MagicMock()
        custom_embedding_processor.get_embedding_function.return_value = custom_embedding_function
        
        # Сбрасываем счетчики вызовов
        self.mock_embedding_processor_class.reset_mock()
        
        chroma_manager = ChromaDBManager(embedding_processor=custom_embedding_processor)
        
        # Check that the provided embedding processor is used
        self.assertEqual(chroma_manager.embedding_processor, custom_embedding_processor)
        self.assertEqual(chroma_manager.embedding_function, custom_embedding_function)
        
        # Verify embedding processor wasn't created again
        self.mock_embedding_processor_class.assert_not_called()

    def test_list_collections(self):
        """Test listing collections"""
        # Configure mock
        mock_collections = [MagicMock(), MagicMock()]
        self.mock_chroma_client.list_collections.return_value = mock_collections
        
        # Test the method
        result = self.chroma_manager.list_collections()
        
        # Check the method was called
        self.mock_chroma_client.list_collections.assert_called_once()
        
        # Check the result
        self.assertEqual(result, mock_collections)

    def test_list_collections_error(self):
        """Test listing collections with error"""
        # Configure mock to raise exception
        self.mock_chroma_client.list_collections.side_effect = Exception("Test error")
        
        # Test the method
        result = self.chroma_manager.list_collections()
        
        # Check the result is an empty list on error
        self.assertEqual(result, [])

    def test_create_collection_new(self):
        """Test creating a new collection"""
        # Configure mock to raise exception first (collection doesn't exist)
        # and then return a new collection
        mock_collection = MagicMock()
        self.mock_chroma_client.get_collection.side_effect = Exception("Collection not found")
        self.mock_chroma_client.create_collection.return_value = mock_collection
        
        # Test the method
        result = self.chroma_manager.create_collection("test_collection", {"key": "value"})
        
        # Check the method was called with correct parameters
        self.mock_chroma_client.get_collection.assert_called_once_with(
            name="test_collection",
            embedding_function=self.mock_embedding_function
        )
        self.mock_chroma_client.create_collection.assert_called_once_with(
            name="test_collection",
            metadata={"key": "value"},
            embedding_function=self.mock_embedding_function
        )
        
        # Check the result
        self.assertEqual(result, mock_collection)

    def test_create_collection_existing(self):
        """Test creating a collection that already exists"""
        # Configure mock to return an existing collection
        mock_collection = MagicMock()
        self.mock_chroma_client.get_collection.return_value = mock_collection
        
        # Test the method
        result = self.chroma_manager.create_collection("test_collection")
        
        # Check get_collection was called but create_collection was not
        self.mock_chroma_client.get_collection.assert_called_once()
        self.mock_chroma_client.create_collection.assert_not_called()
        
        # Check the result
        self.assertEqual(result, mock_collection)

    def test_get_collection(self):
        """Test getting a collection"""
        # Configure mock
        mock_collection = MagicMock()
        self.mock_chroma_client.get_collection.return_value = mock_collection
        
        # Test the method
        result = self.chroma_manager.get_collection("test_collection")
        
        # Check the method was called with correct parameters
        self.mock_chroma_client.get_collection.assert_called_once_with(
            name="test_collection",
            embedding_function=self.mock_embedding_function
        )
        
        # Check the result
        self.assertEqual(result, mock_collection)

    def test_get_collection_error(self):
        """Test getting a collection that doesn't exist"""
        # Configure mock to raise exception
        self.mock_chroma_client.get_collection.side_effect = Exception("Collection not found")
        
        # Test the method
        result = self.chroma_manager.get_collection("non_existent_collection")
        
        # Check the result is None
        self.assertIsNone(result)

    def test_add_documents(self):
        """Test adding documents to a collection"""
        # Configure mocks
        mock_collection = MagicMock()
        mock_collection.add.return_value = None
        
        # Создаем патч для метода get_collection вместо переопределения
        with patch.object(self.chroma_manager, 'get_collection', return_value=mock_collection):
            documents = ["document1", "document2"]
            metadatas = [{"source": "source1"}, {"source": "source2"}]
            ids = ["id1", "id2"]
            
            # Test the method
            result = self.chroma_manager.add_documents(
                collection_name="test_collection",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Check the collection was retrieved
            self.chroma_manager.get_collection.assert_called_once_with("test_collection")
            
            # Check documents were added with correct parameters
            mock_collection.add.assert_called_once_with(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Check the result is True (success)
            self.assertTrue(result)

    def test_add_documents_no_ids(self):
        """Test adding documents without providing IDs"""
        # Configure mocks
        mock_collection = MagicMock()
        
        # Создаем патч для метода get_collection вместо переопределения
        with patch.object(self.chroma_manager, 'get_collection', return_value=mock_collection):
            documents = ["document1", "document2"]
            metadatas = [{"source": "source1"}, {"source": "source2"}]
            
            # Test the method
            result = self.chroma_manager.add_documents(
                collection_name="test_collection",
                documents=documents,
                metadatas=metadatas
            )
            
            # Check documents were added with generated IDs
            mock_collection.add.assert_called_once_with(
                documents=documents,
                metadatas=metadatas,
                ids=["id0", "id1"]
            )
            
            # Check the result is True (success)
            self.assertTrue(result)

    def test_add_documents_collection_not_found(self):
        """Test adding documents to a non-existent collection"""
        # Создаем патч для метода get_collection вместо переопределения
        with patch.object(self.chroma_manager, 'get_collection', return_value=None):
            # Test the method
            result = self.chroma_manager.add_documents(
                collection_name="non_existent_collection",
                documents=["document"]
            )
            
            # Check the result is False (failure)
            self.assertFalse(result)

    def test_get_collection_contents(self):
        """Test getting contents of a collection"""
        # Configure mocks
        mock_collection = MagicMock()
        mock_contents = {
            "ids": ["id1", "id2"],
            "documents": ["document1", "document2"],
            "metadatas": [{"source": "source1"}, {"source": "source2"}]
        }
        mock_collection.get.return_value = mock_contents
        
        # Используем with patch чтобы не вызывать ошибку с super()
        with patch.object(self.chroma_manager, 'get_collection', return_value=mock_collection):
            # Test the method
            result = self.chroma_manager.get_collection_contents("test_collection")
            
            # Check the collection was retrieved
            self.chroma_manager.get_collection.assert_called_once_with("test_collection")
            
            # Check get was called with correct parameters
            mock_collection.get.assert_called_once_with(include=["documents", "metadatas"])
            
            # Check the result contains the expected contents
            self.assertEqual(result, mock_contents)

    def test_get_collection_contents_with_include(self):
        """Test getting contents with specific include parameters"""
        # Configure mocks
        mock_collection = MagicMock()
        mock_collection.get.return_value = {"ids": ["id1", "id2"]}
        
        # Используем with patch чтобы не вызывать ошибку с super()
        with patch.object(self.chroma_manager, 'get_collection', return_value=mock_collection):
            # Test the method with custom include parameter
            result = self.chroma_manager.get_collection_contents(
                collection_name="test_collection",
                include=["ids"]
            )
            
            # Check get was called with correct parameters
            mock_collection.get.assert_called_once_with(include=["ids"])

    def test_get_collection_contents_collection_not_found(self):
        """Test getting contents from a non-existent collection"""
        # Используем with patch чтобы не вызывать ошибку с super()
        with patch.object(self.chroma_manager, 'get_collection', return_value=None):
            # Test the method
            result = self.chroma_manager.get_collection_contents("non_existent_collection")
            
            # Check the result is an empty dictionary
            self.assertEqual(result, {})

    def test_delete_all_collections(self):
        """Test deleting all collections"""
        # Configure mocks
        mock_collection1 = MagicMock()
        mock_collection1.name = "collection1"
        mock_collection2 = MagicMock()
        mock_collection2.name = "collection2"
        
        # Используем with patch чтобы не вызывать ошибку с super()
        with patch.object(self.chroma_manager, 'list_collections', return_value=[mock_collection1, mock_collection2]):
            # Test the method
            result = self.chroma_manager.delete_all_collections()
            
            # Check collections were listed
            self.chroma_manager.list_collections.assert_called_once()
            
            # Check each collection was deleted
            self.mock_chroma_client.delete_collection.assert_any_call(name="collection1")
            self.mock_chroma_client.delete_collection.assert_any_call(name="collection2")
            self.assertEqual(self.mock_chroma_client.delete_collection.call_count, 2)
            
            # Check the result contains the expected summary
            self.assertEqual(result["success"], True)
            self.assertEqual(result["total"], 2)
            self.assertEqual(result["deleted"], 2)
            self.assertEqual(result["failed"], 0)
            self.assertEqual(result["failed_collections"], [])

    def test_delete_all_collections_no_collections(self):
        """Test deleting all collections when none exist"""
        # Используем with patch чтобы не вызывать ошибку с super()
        with patch.object(self.chroma_manager, 'list_collections', return_value=[]):
            # Test the method
            result = self.chroma_manager.delete_all_collections()
            
            # Check delete_collection was not called
            self.mock_chroma_client.delete_collection.assert_not_called()
            
            # Check the result contains the expected summary
            self.assertEqual(result["success"], True)
            self.assertEqual(result["total"], 0)
            self.assertEqual(result["deleted"], 0)


if __name__ == '__main__':
    unittest.main() 
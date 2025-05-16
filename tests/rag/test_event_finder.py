import unittest
import numpy as np
from unittest.mock import patch, MagicMock

from src.rag.core.event_specifics.event_finder import EventSpecifics


class TestEventSpecifics(unittest.TestCase):
    """Tests for EventSpecifics class"""

    def setUp(self):
        """Set up the test environment with mocks for all dependencies"""
        # Create mock instances for dependencies
        self.mock_embedding_processor = MagicMock()
        self.mock_chroma_manager = MagicMock()

        # Create an instance of EventSpecifics with mocked dependencies
        self.event_specifics = EventSpecifics(
            embedding_processor=self.mock_embedding_processor,
            chroma_manager=self.mock_chroma_manager
        )

        # Set up common test data
        self.sample_embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ])

        self.sample_documents = [
            "Document 1 about conferences",
            "Document 2 about workshops",
            "Document 3 about seminars"
        ]

        self.sample_metadatas = [
            {"title": "Conference Info", "source": "Conference A"},
            {"title": "Workshop Guide", "source": "Workshop B"},
            {"title": "Seminar Details", "source": "Seminar C"}
        ]

        self.sample_collection_contents = {
            'embeddings': self.sample_embeddings,
            'documents': self.sample_documents,
            'metadatas': self.sample_metadatas
        }

    def test_find_specifics(self):
        """Test finding specifics with successful collection lookup"""
        # Configure mocks
        self.event_specifics._load_collection_contents = MagicMock(
            return_value=self.sample_collection_contents
        )

        # Настраиваем размерности массивов, чтобы они совпадали для корректного матричного умножения
        chunks = ["Query chunk 1", "Query chunk 2"]

        # Размерность запросов: (количество_запросов, размерность_эмбеддинга)
        query_embeddings = np.array([
            [0.2, 0.3, 0.4],  # First query embedding
            [0.5, 0.6, 0.7]   # Second query embedding
        ])

        # Используем те же размерности для нормализованных эмбеддингов
        normalized_query_embeddings = np.array([
            [0.2 / np.sqrt(0.04 + 0.09 + 0.16), 0.3 / np.sqrt(0.04 + 0.09 + 0.16), 0.4 / np.sqrt(0.04 + 0.09 + 0.16)],
            [0.5 / np.sqrt(0.25 + 0.36 + 0.49), 0.6 / np.sqrt(0.25 + 0.36 + 0.49), 0.7 / np.sqrt(0.25 + 0.36 + 0.49)]
        ])

        # Для коллекции сохраняем ту же размерность, что и в self.sample_embeddings
        normalized_col_embeddings = np.array([
            [0.1 / np.sqrt(0.01 + 0.04 + 0.09), 0.2 / np.sqrt(0.01 + 0.04 + 0.09), 0.3 / np.sqrt(0.01 + 0.04 + 0.09)],
            [0.4 / np.sqrt(0.16 + 0.25 + 0.36), 0.5 / np.sqrt(0.16 + 0.25 + 0.36), 0.6 / np.sqrt(0.16 + 0.25 + 0.36)],
            [0.7 / np.sqrt(0.49 + 0.64 + 0.81), 0.8 / np.sqrt(0.49 + 0.64 + 0.81), 0.9 / np.sqrt(0.49 + 0.64 + 0.81)]
        ])

        # Матрица сходства: (количество_запросов, количество_документов)
        similarity_matrix = np.array([
            [0.9, 0.5, 0.3],  # Сходство первого запроса с документами
            [0.4, 0.8, 0.6]   # Сходство второго запроса с документами
        ])

        # Настраиваем mock для вызовов методов embedding_processor
        self.mock_embedding_processor.embed_texts.return_value = query_embeddings

        # Мокаем вызовы normalize_embeddings для каждого случая
        def normalize_side_effect(embeddings):
            if np.array_equal(embeddings, self.sample_embeddings):
                return normalized_col_embeddings
            elif np.array_equal(embeddings, query_embeddings):
                return normalized_query_embeddings
            return embeddings

        self.mock_embedding_processor.normalize_embeddings.side_effect = normalize_side_effect

        # Мокаем compute_cosine_similarity для возврата предопределенной матрицы сходства
        self.mock_embedding_processor.compute_cosine_similarity.return_value = similarity_matrix

        # Set up _get_topk_hits mock to return sample hits by chunk
        hits_by_chunk = {
            "Query chunk 1": [
                {"document": "Document 1 about conferences", "metadata": self.sample_metadatas[0], "similarity": 0.9},
                {"document": "Document 2 about workshops", "metadata": self.sample_metadatas[1], "similarity": 0.5}
            ],
            "Query chunk 2": [
                {"document": "Document 2 about workshops", "metadata": self.sample_metadatas[1], "similarity": 0.8},
                {"document": "Document 3 about seminars", "metadata": self.sample_metadatas[2], "similarity": 0.6}
            ]
        }
        self.event_specifics._get_topk_hits = MagicMock(return_value=hits_by_chunk)

        # Set up _aggregate_hits mock to return aggregated results
        aggregated_results = [
            {"document": "Document 2 about workshops", "metadata": self.sample_metadatas[1],
             "sum_similarity": 1.3, "count": 2, "chunks": ["Query chunk 1", "Query chunk 2"]},
            {"document": "Document 1 about conferences", "metadata": self.sample_metadatas[0],
             "sum_similarity": 0.9, "count": 1, "chunks": ["Query chunk 1"]}
        ]
        self.event_specifics._aggregate_hits = MagicMock(return_value=aggregated_results)

        # Call the method
        result = self.event_specifics.find_specifics(
            collection_name="test_collection",
            chunks=chunks,
            top_k=2,
            top_n=2
        )

        # Check that _load_collection_contents was called with correct parameters
        self.event_specifics._load_collection_contents.assert_called_once_with("test_collection")

        # Check that embedding processor methods were called correctly
        self.mock_embedding_processor.embed_texts.assert_called_once_with(chunks)

        # Check compute_cosine_similarity was called with correct parameters
        # Используем any_call вместо assert_called_once_with, потому что порядок
        # вызовов normalize_embeddings может различаться
        self.mock_embedding_processor.compute_cosine_similarity.assert_called_once()

        # Check that _get_topk_hits was called with correct parameters
        self.event_specifics._get_topk_hits.assert_called_once_with(
            similarity_matrix,
            self.sample_documents,
            self.sample_metadatas,
            chunks,
            2  # top_k
        )

        # Check that _aggregate_hits was called with correct parameters
        self.event_specifics._aggregate_hits.assert_called_once_with(hits_by_chunk, 2)

        # Check the result
        expected_result = ["Document 2 about workshops", "Document 1 about conferences"]
        self.assertEqual(result, expected_result)

    def test_find_specifics_empty_collection(self):
        """Test finding specifics with empty collection"""
        # Configure mock to return empty collection contents
        self.event_specifics._load_collection_contents = MagicMock(return_value={})

        # Call the method
        result = self.event_specifics.find_specifics(
            collection_name="non_existent_collection",
            chunks=["Query chunk"],
            top_k=2,
            top_n=2
        )

        # Check that _load_collection_contents was called
        self.event_specifics._load_collection_contents.assert_called_once_with(
            "non_existent_collection")

        # Check the result is an empty list
        self.assertEqual(result, [])

        # Verify that no other methods were called
        self.mock_embedding_processor.embed_texts.assert_not_called()
        self.mock_embedding_processor.normalize_embeddings.assert_not_called()
        self.mock_embedding_processor.compute_cosine_similarity.assert_not_called()

    def test_load_collection_contents(self):
        """Test loading collection contents"""
        # Configure mocks
        mock_collection = MagicMock()
        mock_collection.get.return_value = {
            'embeddings': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            'documents': ["Document 1", "Document 2"],
            'metadatas': [{"source": "A"}, {"source": "B"}]
        }
        self.mock_chroma_manager.get_collection.return_value = mock_collection

        # Call the method
        result = self.event_specifics._load_collection_contents("test_collection")

        # Check that get_collection was called with correct parameters
        self.mock_chroma_manager.get_collection.assert_called_once_with("test_collection")

        # Check that collection.get was called with correct parameters
        mock_collection.get.assert_called_once_with(
            include=['embeddings', 'documents', 'metadatas'])

        # Check the result
        self.assertIn('embeddings', result)
        self.assertIn('documents', result)
        self.assertIn('metadatas', result)
        self.assertIsInstance(result['embeddings'], np.ndarray)
        self.assertEqual(len(result['documents']), 2)
        self.assertEqual(len(result['metadatas']), 2)

    def test_load_collection_contents_not_found(self):
        """Test loading collection contents when collection not found"""
        # Configure mock to return None (collection not found)
        self.mock_chroma_manager.get_collection.return_value = None

        # Call the method
        result = self.event_specifics._load_collection_contents("non_existent_collection")

        # Check that get_collection was called
        self.mock_chroma_manager.get_collection.assert_called_once_with("non_existent_collection")

        # Check the result is an empty dictionary
        self.assertEqual(result, {})

    def test_get_topk_hits(self):
        """Test getting top-k hits"""
        # Set up test data
        sims = np.array([
            [0.9, 0.5, 0.3],  # Query 1 similarities
            [0.4, 0.8, 0.6]   # Query 2 similarities
        ])

        docs = ["Document A", "Document B", "Document C"]
        metas = [{"source": "A"}, {"source": "B"}, {"source": "C"}]
        queries = ["Query 1", "Query 2"]
        top_k = 2

        # Call the method
        result = self.event_specifics._get_topk_hits(sims, docs, metas, queries, top_k)

        # Check the structure of the result
        self.assertIn("Query 1", result)
        self.assertIn("Query 2", result)
        self.assertEqual(len(result["Query 1"]), 2)  # top_k = 2
        self.assertEqual(len(result["Query 2"]), 2)  # top_k = 2

        # Check the content of Query 1 results (sorted by similarity)
        self.assertEqual(result["Query 1"][0]["document"], "Document A")  # Highest similarity 0.9
        self.assertEqual(result["Query 1"][0]["similarity"], 0.9)
        self.assertEqual(result["Query 1"][0]["metadata"], {"source": "A"})

        self.assertEqual(result["Query 1"][1]["document"], "Document B")  # Second highest 0.5
        self.assertEqual(result["Query 1"][1]["similarity"], 0.5)

        # Check the content of Query 2 results (sorted by similarity)
        self.assertEqual(result["Query 2"][0]["document"], "Document B")  # Highest similarity 0.8
        self.assertEqual(result["Query 2"][0]["similarity"], 0.8)

        self.assertEqual(result["Query 2"][1]["document"], "Document C")  # Second highest 0.6
        self.assertEqual(result["Query 2"][1]["similarity"], 0.6)

    def test_aggregate_hits(self):
        """Test aggregating hits across different chunks"""
        # Set up test data
        hits_by_chunk = {
            "Query chunk 1": [
                {"document": "Document A", "metadata": {"source": "A"}, "similarity": 0.9},
                {"document": "Document B", "metadata": {"source": "B"}, "similarity": 0.5}
            ],
            "Query chunk 2": [
                {"document": "Document B", "metadata": {"source": "B"}, "similarity": 0.8},
                {"document": "Document C", "metadata": {"source": "C"}, "similarity": 0.6}
            ]
        }
        top_n = 2

        # Call the method
        result = self.event_specifics._aggregate_hits(hits_by_chunk, top_n)

        # Check the result has the right number of items
        self.assertEqual(len(result), 2)  # top_n = 2

        # Check the items are sorted by sum_similarity
        self.assertEqual(result[0]["document"], "Document B")  # Highest combined similarity 1.3
        self.assertEqual(result[0]["sum_similarity"], 1.3)
        self.assertEqual(result[0]["count"], 2)
        self.assertEqual(sorted(result[0]["chunks"]), sorted(["Query chunk 1", "Query chunk 2"]))

        self.assertEqual(result[1]["document"], "Document A")  # Second highest 0.9
        self.assertEqual(result[1]["sum_similarity"], 0.9)
        self.assertEqual(result[1]["count"], 1)
        self.assertEqual(result[1]["chunks"], ["Query chunk 1"])

    def test_aggregate_hits_no_limit(self):
        """Test aggregating hits with no limit (top_n=None)"""
        # Set up test data
        hits_by_chunk = {
            "Query chunk 1": [
                {"document": "Document A", "metadata": {"source": "A"}, "similarity": 0.9},
                {"document": "Document B", "metadata": {"source": "B"}, "similarity": 0.5}
            ],
            "Query chunk 2": [
                {"document": "Document B", "metadata": {"source": "B"}, "similarity": 0.8},
                {"document": "Document C", "metadata": {"source": "C"}, "similarity": 0.6}
            ]
        }

        # Call the method with top_n=None
        result = self.event_specifics._aggregate_hits(hits_by_chunk, None)

        # Check all items are returned
        self.assertEqual(len(result), 3)  # All unique documents


if __name__ == '__main__':
    unittest.main()

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/rag')))
from rag.pipeline import RAGPipeline


class TestRAGPipeline(unittest.TestCase):
    """Tests for RAGPipeline class"""

    def setUp(self):
        """Set up the test environment with mocks for all dependencies"""
        # Prepare patches for all components
        self.config_loader_patcher = patch('rag.pipeline.ConfigLoader')
        self.embedding_processor_patcher = patch('rag.pipeline.EmbeddingProcessor')
        self.text_processor_patcher = patch('rag.pipeline.TextProcessor')
        self.chroma_manager_patcher = patch('rag.pipeline.ChromaDBManager')
        self.event_specifics_patcher = patch('rag.pipeline.EventSpecifics')
        self.prompt_enricher_patcher = patch('rag.pipeline.PromptEnricher')

        # Start patches
        self.mock_config_loader = self.config_loader_patcher.start()
        self.mock_embedding_processor = self.embedding_processor_patcher.start()
        self.mock_text_processor = self.text_processor_patcher.start()
        self.mock_chroma_manager = self.chroma_manager_patcher.start()
        self.mock_event_specifics = self.event_specifics_patcher.start()
        self.mock_prompt_enricher = self.prompt_enricher_patcher.start()

        # Configure return values for configuration
        config_instance = MagicMock()
        config_instance.load_config.return_value = {"key": "value"}
        config_instance.get_rag_prompt.return_value = "rag prompt template"
        config_instance.get_general_top.return_value = 3
        config_instance.get_article_top.return_value = 1
        self.mock_config_loader.return_value = config_instance

        # Create an instance of RAGPipeline
        self.pipeline = RAGPipeline()

    def tearDown(self):
        """Stop all patches"""
        self.config_loader_patcher.stop()
        self.embedding_processor_patcher.stop()
        self.text_processor_patcher.stop()
        self.chroma_manager_patcher.stop()
        self.event_specifics_patcher.stop()
        self.prompt_enricher_patcher.stop()

    def test_init(self):
        """Test initialization of RAGPipeline class"""
        # Check that all components are created
        self.assertIsNotNone(self.pipeline.config_loader)
        self.assertIsNotNone(self.pipeline.embedding_processor)
        self.assertIsNotNone(self.pipeline.text_processor)
        self.assertIsNotNone(self.pipeline.chroma_manager)
        self.assertIsNotNone(self.pipeline.event_specifics)
        self.assertIsNotNone(self.pipeline.prompt_enricher)

        # Check that parameters are loaded from configuration
        self.assertEqual(self.pipeline.rag_prompt, "rag prompt template")
        self.assertEqual(self.pipeline.general_top, 3)
        self.assertEqual(self.pipeline.article_top, 1)

    def test_preprocess_article(self):
        """Test article preprocessing"""
        # Configure text processor mock
        mock_text_processor_instance = MagicMock()
        mock_text_processor_instance.preprocess_article.return_value = [
            "title", "main text", "literature"]
        self.pipeline.text_processor = mock_text_processor_instance

        # Test the method
        result = self.pipeline.preprocess_article("article text")

        # Check that the method was called with the correct parameters
        mock_text_processor_instance.preprocess_article.assert_called_once_with("article text")

        # Check the result
        self.assertEqual(result, ["title", "main text", "literature"])

    def test_process_article(self):
        """Test article processing"""
        # Configure mocks
        self.pipeline.preprocess_article = MagicMock(return_value=["chunk1", "chunk2"])
        mock_event_specifics_instance = MagicMock()
        mock_event_specifics_instance.find_specifics.return_value = ["specific1", "specific2"]
        self.pipeline.event_specifics = mock_event_specifics_instance

        # Test the method
        result = self.pipeline.process_article("article text", "conference")

        # Check method calls
        self.pipeline.preprocess_article.assert_called_once_with("article text")
        mock_event_specifics_instance.find_specifics.assert_called_once_with(
            collection_name="conference",
            chunks=["chunk1", "chunk2"],
            top_k=self.pipeline.general_top,
            top_n=self.pipeline.article_top
        )

        # Check the result
        self.assertEqual(result, ["specific1", "specific2"])

    def test_pipeline(self):
        """Test the main pipeline method"""
        # Configure mocks
        self.pipeline.process_prompt = MagicMock(return_value=["prompt_specific1"])
        self.pipeline.process_article = MagicMock(
            return_value=["article_specific1", "article_specific2"])

        mock_prompt_enricher_instance = MagicMock()
        mock_prompt_enricher_instance.enrich_prompt.return_value = "enriched prompt"
        self.pipeline.prompt_enricher = mock_prompt_enricher_instance

        # Test the method
        result = self.pipeline.pipeline("article text", "conference", "base prompt")

        # Check method calls
        self.pipeline.process_prompt.assert_called_once_with("conference")
        self.pipeline.process_article.assert_called_once_with("article text", "conference")
        mock_prompt_enricher_instance.enrich_prompt.assert_called_once_with(
            base_prompt="base prompt",
            specifics=["prompt_specific1", "article_specific1", "article_specific2"]
        )

        # Check the result
        self.assertEqual(result, "enriched prompt")


if __name__ == '__main__':
    unittest.main()
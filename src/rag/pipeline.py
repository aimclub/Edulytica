from typing import List
from loguru import logger
from src.rag.core.utils.config_loader import ConfigLoader
from src.rag.core.text_processor.text_processor import TextProcessor
from src.rag.core.chroma_db.chroma_manager import ChromaDBManager
from src.rag.core.event_specifics.event_finder import EventSpecifics
from src.rag.core.prompt_enricher.prompt_enricher import PromptEnricher
from src.rag.core.embedder.embedding_processor import EmbeddingProcessor


class RAGPipeline:
    """
    Main class for implementing the RAG pipeline
    :param self: Instance of RAGPipeline
    """

    def __init__(self):
        """
        Initialize all components of the RAG pipeline
        :param self: Instance of RAGPipeline

        :return: None
        """
        # Load configuration
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_config()

        # Initialize components
        self.embedding_processor = EmbeddingProcessor()
        self.text_processor = TextProcessor()
        self.chroma_manager = ChromaDBManager(embedding_processor=self.embedding_processor)
        self.event_specifics = EventSpecifics(self.embedding_processor, self.chroma_manager)
        self.prompt_enricher = PromptEnricher()

        # Load parameters from configuration
        self.rag_prompt = self.config_loader.get_rag_prompt()
        self.general_top = self.config_loader.get_general_top()
        self.article_top = self.config_loader.get_article_top()

    def preprocess_article(self, text: str) -> List[str]:
        """
        Process article text and split it into parts for analysis
        :param text: Article text

        :return: List of article parts for processing
        """
        # Use the function from Text Processor to preprocess the article
        chunks = self.text_processor.preprocess_article(text)
        logger.info(f"Preprocessed article into {len(chunks)} chunks")
        return chunks

    def process_article(self, article_text: str, conference_name: str) -> List[str]:
        """
        Main method for getting specifics for an article
        :param article_text: Text of the article
        :param conference_name: Name of the conference

        :return: List of specific information
        """
        chunks = self.preprocess_article(article_text)
        return self.event_specifics.find_specifics(
            collection_name=conference_name,
            chunks=chunks,
            top_k=self.general_top,
            top_n=self.article_top
        )

    def process_prompt(self, conference_name: str) -> List[str]:
        """
        Get specifics for the RAG prompt
        :param conference_name: Name of the conference

        :return: List of specific information
        """
        return self.event_specifics.find_specifics(  # pragma: no cover
            collection_name=conference_name,
            chunks=[self.rag_prompt],
            top_k=self.general_top,
            top_n=self.general_top
        )

    def pipeline(self, article_text: str, conference_name: str, prompt: str) -> str:
        """
        Main pipeline method that processes the article and prompt
        :param article_text: Article text to process
        :param conference_name: Name of the conference
        :param prompt: Base prompt to enrich

        :return: Enriched prompt with context-specific information
        """
        # Get specifics for prompt and article
        prompt_specifics = self.process_prompt(conference_name)
        article_specifics = self.process_article(article_text, conference_name)
        # Combine all specifics
        all_specifics = prompt_specifics + article_specifics
        # Form enriched prompt
        return self.prompt_enricher.enrich_prompt(base_prompt=prompt, specifics=all_specifics)

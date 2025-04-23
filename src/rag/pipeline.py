from typing import List
from loguru import logger
from core.utils.config_loader import ConfigLoader
from core.text_processor.text_processor import TextProcessor
from core.chroma_db.chroma_manager import ChromaDBManager
from core.event_specifics.event_finder import EventSpecifics
from core.prompt_enricher.prompt_enricher import PromptEnricher
from core.embedder.embedding_processor import EmbeddingProcessor

class RAGPipeline:
    """
    Main class for implementing the RAG pipeline.
    Includes text processing, searching for relevant data in ChromaDB,
    extracting event specifics, and enriching prompts.
    """
    
    def __init__(self):
        """
        Initialize all components of the RAG pipeline
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
        Process article text and split it into parts for analysis.
        
        Args:
            text: Article text
            
        Returns:
            List of article parts for processing
        """
        # Use the function from Text Processor to preprocess the article
        chunks = self.text_processor.preprocess_article(text)
        logger.info(f"Preprocessed article into {len(chunks)} chunks")
        return chunks

    
    def process_article(self, article_text: str, conference_name: str) -> List[str]:
        """
        Main method for getting specifics for an article.
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
        """
        return self.event_specifics.find_specifics(
            collection_name=conference_name,
            chunks=[self.rag_prompt],
            top_k=self.general_top,
            top_n=self.general_top
        )
    
    def pipeline(self, article_text: str, conference_name: str, prompt: str) -> str:
        """
        Main pipeline method that processes the article and prompt
        
        Args:
            article_text: Article text to process
            conference_name: Name of the conference
            prompt: Base prompt to enrich
            
        Returns:
            Enriched prompt with context-specific information
        """
        # Get specifics for prompt and article
        prompt_specifics = self.process_prompt(conference_name)
        article_specifics = self.process_article(article_text, conference_name)
        # Combine all specifics
        all_specifics = prompt_specifics + article_specifics
        # Form enriched prompt
        return self.prompt_enricher.enrich_prompt(base_prompt=prompt, specifics=all_specifics)
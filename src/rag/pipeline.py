import sys
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger
import numpy as np

# Import system components
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
    
    def search_by_embedding(self, 
                           collection_name: str, 
                           queries: List[str], 
                           top_k: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform search by embeddings in the specified collection.
        
        Args:
            collection_name: Collection name in ChromaDB
            queries: List of queries
            top_k: Number of results to return
            
        Returns:
            Dictionary with search results for each query
        """
        # Load collection
        contents = self._load_collection_contents(collection_name)
        if not contents or 'embeddings' not in contents:
            logger.error(f"Failed to load contents from collection {collection_name}")
            return {}
        
        # Normalize collection embeddings
        col_embs_norm = self.embedding_processor.normalize_embeddings(contents['embeddings'])
        
        # Get query embeddings
        q_embs = self.embedding_processor.embed_texts(queries)
        q_embs_norm = self.embedding_processor.normalize_embeddings(q_embs)
        
        # Calculate similarity matrix
        sims = self.embedding_processor.compute_cosine_similarity(q_embs_norm, col_embs_norm)
        
        # Collect results
        results = self._get_topk_hits(
            sims, 
            contents['documents'], 
            contents['metadatas'], 
            queries, 
            top_k
        )
        
        logger.info(f"Found {len(results)} results for queries in collection {collection_name}")
        return results
    
    def _load_collection_contents(self, collection_name: str) -> Dict[str, Any]:
        """
        Load collection contents from ChromaDB.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Dictionary with embeddings, documents, and metadata
        """
        collection = self.chroma_manager.get_collection(collection_name)
        if collection is None:
            logger.error(f"Collection '{collection_name}' not found")
            return {}
        
        contents = collection.get(include=['embeddings', 'documents', 'metadatas'])
        return {
            'embeddings': np.array(contents['embeddings']),
            'documents': contents['documents'],
            'metadatas': contents['metadatas']
        }
    
    def _get_topk_hits(self, 
                      sims: np.ndarray, 
                      docs: List[str], 
                      metas: List[dict], 
                      queries: List[str], 
                      top_k: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        For each query, returns top-k documents with metadata and similarity.
        
        Args:
            sims: Cosine similarity matrix
            docs: List of documents
            metas: List of metadata
            queries: List of queries
            top_k: Number of results to return
            
        Returns:
            Dictionary query -> list of results
        """
        results: Dict[str, List[Dict[str, Any]]] = {}
        for qi, query in enumerate(queries):
            sim_row = sims[qi]
            best_idxs = np.argsort(-sim_row)[:top_k]
            hits = []
            for idx in best_idxs:
                hits.append({
                    'document': docs[idx],
                    'metadata': metas[idx],
                    'similarity': float(sim_row[idx])
                })
            results[query] = hits
        return results
    
    def aggregate_hits(self, 
                      hits_by_chunk: Dict[str, List[Dict[str, Any]]], 
                      top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Aggregates search results across different chunks and returns top-n.
        
        Args:
            hits_by_chunk: Search results by chunk
            top_n: Number of results to return
            
        Returns:
            List of aggregated results
        """
        agg: Dict[str, Dict[str, Any]] = {}

        for chunk, hits in hits_by_chunk.items():
            for hit in hits:
                doc = hit['document']
                sim = hit['similarity']
                md = hit['metadata']

                if doc not in agg:
                    agg[doc] = {
                        'document': doc,
                        'metadata': md,
                        'sum_similarity': sim,
                        'count': 1,
                        'chunks': [chunk]
                    }
                else:
                    agg_entry = agg[doc]
                    agg_entry['sum_similarity'] += sim
                    agg_entry['count'] += 1
                    agg_entry['chunks'].append(chunk)

        # Convert to list and sort by descending sum_similarity
        aggregated_list = sorted(
            agg.values(),
            key=lambda x: x['sum_similarity'],
            reverse=True
        )

        if top_n is not None:
            return aggregated_list[:top_n]
        return aggregated_list
    
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
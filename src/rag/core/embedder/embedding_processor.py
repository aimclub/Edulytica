import chromadb
import numpy as np
import pandas as pd
from copy import deepcopy
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from ..utils.config_loader import ConfigLoader

class EmbeddingProcessor:
    """
    Class for creating and processing embeddings from text data
    """
    def __init__(self, embedding_model: Optional[str] = None):
        """
        Initialization with embedding model selection
        
        Args:
            embedding_model: Name of the model for creating embeddings (optional)
                            If not specified, the model from the configuration will be used
        """
        config_loader = ConfigLoader()
        self.embedding_model = embedding_model or config_loader.get_embedding_model()
        logger.info(f"Initializing EmbeddingProcessor with model: {self.embedding_model}")
        
        try:
            self.embedding_function = chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model)
            logger.info(f"Successfully initialized embedding function with model {self.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding function: {e}")
            raise
    
    def get_embedding_function(self):
        """
        Get the function for creating embeddings
        
        Returns:
            Function for creating embeddings
        """
        return self.embedding_function
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Creates embeddings for a list of texts
        
        Args:
            texts: List of texts for embedding
            
        Returns:
            Array of embeddings with shape (n_texts, embedding_dim)
        """
        try:
            embeddings = self.embedding_function(texts)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        L2-normalizes embeddings along each row
        
        Args:
            embeddings: Array of embeddings
            
        Returns:
            Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / np.where(norms == 0, 1, norms)
    
    def compute_cosine_similarity(self, 
                                 query_embeddings: np.ndarray, 
                                 document_embeddings: np.ndarray) -> np.ndarray:
        """
        Computes cosine similarity between queries and documents
        
        Args:
            query_embeddings: Query embeddings with shape (n_queries, embedding_dim)
            document_embeddings: Document embeddings with shape (n_docs, embedding_dim)
            
        Returns:
            Cosine similarity matrix with shape (n_queries, n_docs)
        """
        # Normalize embeddings for cosine similarity
        query_norm = self.normalize_embeddings(query_embeddings)
        doc_norm = self.normalize_embeddings(document_embeddings)
        
        # Compute cosine similarity as the dot product of normalized vectors
        return query_norm.dot(doc_norm.T)
    
    def process_excel_data(self, file_name: str, sheet_name: str) -> Dict[str, Any]:
        """
        Process Excel file and prepare data for embeddings
        
        Args:
            file_name: Path to the Excel file
            sheet_name: Sheet name in the Excel file
            
        Returns:
            Dictionary with structured data for saving to ChromaDB
        """
        logger.info(f"Processing Excel data from file: {file_name}, sheet: {sheet_name}")
        
        try:
            # Read data from Excel
            spec_data = pd.read_excel(file_name, sheet_name=sheet_name, header=[0,1,2,3])
            spec_data = spec_data.fillna("")
            logger.info(f"Successfully read Excel data with shape: {spec_data.shape}")
            
            # Process data
            res = {}
            res['description_full'] = []
            
            # Process column headers
            for i in spec_data.columns:
                ii = list(i)
                res['description_full'].append({})
                res['description_full'][-1]['column_title'] = ''
                
                for j in range(1, len(ii)):
                    if not (ii[j].startswith("Unnamed")):
                        res['description_full'][-1]['column_title'] += ii[j]
                        res['description_full'][-1]['column_title'] += '__'
                
                res['description_full'][-1]['column_title'] = res['description_full'][-1]['column_title'][:-2]
                res['description_full'][-1]['column_text'] = " ".join(spec_data[i].tolist()).strip()
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for j in range(len(res['description_full'])):
                ids.append(f"id{j}")
                documents.append(res['description_full'][j]['column_text'])
                md = {
                    'column_title': res['description_full'][j]['column_title']
                }
                metadatas.append(deepcopy(md))
            
            # Create collection metadata
            collection_metadata = {
                "source_file": file_name,
                "sheet_name": sheet_name,
                "conf_title": spec_data.columns[0][0],
                "conf_title_short": sheet_name
            }
            
            logger.info(f"Processed {len(documents)} documents from Excel data")
            
            return {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
                "collection_metadata": collection_metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel data: {e}")
            raise 
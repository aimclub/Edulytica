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
        :param embedding_model: Name of the model for creating embeddings
        """
        config_loader = ConfigLoader()  # pragma: no cover
        self.embedding_model = embedding_model or config_loader.get_embedding_model()  # pragma: no cover
        logger.info(
            f"Initializing EmbeddingProcessor with model: {self.embedding_model}")  # pragma: no cover

        try:  # pragma: no cover
            self.embedding_function = chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model)
            logger.info(
                f"Successfully initialized embedding function with model {self.embedding_model}")
        except Exception as e:  # pragma: no cover
            logger.error(f"Failed to initialize embedding function: {e}")
            raise

    def get_embedding_function(self):
        """
        Get the function for creating embeddings

        :return: Function for creating embeddings
        """
        return self.embedding_function  # pragma: no cover

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Creates embeddings for a list of texts
        :param self: Instance of EmbeddingProcessor
        :param texts: List of texts for embedding
        :return: Array of embeddings with shape (n_texts, embedding_dim)
        """
        try:  # pragma: no cover
            embeddings = self.embedding_function(texts)
            return np.array(embeddings)
        except Exception as e:  # pragma: no cover
            logger.error(f"Error creating embeddings: {e}")
            raise

    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        L2-normalizes embeddings along each row
        :param self: Instance of EmbeddingProcessor
        :param embeddings: Array of embeddings
        :return: Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)   # pragma: no cover
        return embeddings / np.where(norms == 0, 1, norms)  # pragma: no cover

    def compute_cosine_similarity(self,
                                  query_embeddings: np.ndarray,
                                  document_embeddings: np.ndarray) -> np.ndarray:
        """
        Computes cosine similarity between queries and documents
        :param self: Instance of EmbeddingProcessor
        :param query_embeddings: Query embeddings with shape (n_queries, embedding_dim)
        :param document_embeddings: Document embeddings with shape (n_docs, embedding_dim)
        :return: Cosine similarity matrix with shape (n_queries, n_docs)
        """
        # Normalize embeddings for cosine similarity
        query_norm = self.normalize_embeddings(query_embeddings)  # pragma: no cover
        doc_norm = self.normalize_embeddings(document_embeddings)  # pragma: no cover

        # Compute cosine similarity as the dot product of normalized vectors
        return query_norm.dot(doc_norm.T)  # pragma: no cover

    def process_excel_data(self, file_name: str, sheet_name: str) -> Dict[str, Any]:
        """
        Process Excel file and prepare data for embeddings
        :param self: Instance of EmbeddingProcessor
        :param file_name: Path to the Excel file
        :param sheet_name: Sheet name in the Excel file
        :return: Dictionary with structured data for saving to ChromaDB
        """
        logger.info(
            f"Processing Excel data from file: {file_name}, sheet: {sheet_name}")  # pragma: no cover

        try:  # pragma: no cover
            # Read data from Excel
            spec_data = pd.read_excel(file_name, sheet_name=sheet_name, header=[0, 1, 2, 3])
            spec_data = spec_data.fillna("")
            logger.info(
                f"Successfully read Excel data with shape: {spec_data.shape}")  # pragma: no cover

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
            }  # pragma: no cover

        except Exception as e:  # pragma: no cover
            logger.error(f"Error processing Excel data: {e}")
            raise

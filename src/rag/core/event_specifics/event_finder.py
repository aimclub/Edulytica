from typing import List, Dict, Any
import numpy as np
from loguru import logger
from core.embedder.embedding_processor import EmbeddingProcessor
from core.chroma_db.chroma_manager import ChromaDBManager


class EventSpecifics:
    """
    Class for finding event specifics using embeddings and aggregating results
    """

    def __init__(self, embedding_processor: EmbeddingProcessor, chroma_manager: ChromaDBManager):
        """
        Initialize EventSpecifics with embedding processor and ChromaDB manager
        :param embedding_processor: Embedding processor instance
        :param chroma_manager: ChromaDB manager instance
        """
        self.embedding_processor = embedding_processor
        self.chroma_manager = chroma_manager

    def find_specifics(
        self,
        collection_name: str,
        chunks: List[str],
        top_k: int,
        top_n: int
    ) -> List[str]:
        """
        Searches for and aggregates results for a list of text chunks
        :param collection_name: Name of the collection to search in
        :param chunks: List of text chunks to search for
        :param top_k: Number of top results per chunk
        :param top_n: Number of top results after aggregation

        :return: List of specific information
        """
        # 1. Load collection contents
        contents = self._load_collection_contents(collection_name)
        if not contents:
            return []
        # 2. Normalize collection embeddings
        col_embs_norm = self.embedding_processor.normalize_embeddings(contents['embeddings'])
        # 3. Create query embeddings and normalize them
        q_embs = self.embedding_processor.embed_texts(chunks)
        q_embs_norm = self.embedding_processor.normalize_embeddings(q_embs)
        # 4. Calculate similarity
        sims = self.embedding_processor.compute_cosine_similarity(q_embs_norm, col_embs_norm)
        # 5. Collect hits by chunk
        hits_by_chunk = self._get_topk_hits(
            sims,
            contents['documents'],
            contents['metadatas'],
            chunks,
            top_k
        )
        # 6. Aggregate results
        aggregated = self._aggregate_hits(hits_by_chunk, top_n)
        # 7. Return list of documents
        return [item['document'] for item in aggregated]

    def _load_collection_contents(self, collection_name: str) -> Dict[str, Any]:
        """
        Load contents from a ChromaDB collection
        :param collection_name: Name of the collection

        :return: Dictionary with embeddings, documents, and metadata
        """
        collection = self.chroma_manager.get_collection(collection_name)
        if collection is None:
            logger.error(f"Collection '{collection_name}' not found")
            return {}
        cont = collection.get(include=['embeddings', 'documents', 'metadatas'])
        return {
            'embeddings': np.array(cont['embeddings']),
            'documents': cont['documents'],
            'metadatas': cont['metadatas']
        }

    def _get_topk_hits(
        self,
        sims: np.ndarray,
        docs: List[str],
        metas: List[dict],
        queries: List[str],
        top_k: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get top-k results for each query
        :param sims: Similarity matrix
        :param docs: List of documents
        :param metas: List of metadata
        :param queries: List of queries
        :param top_k: Number of results to return for each query

        :return: Dictionary mapping queries to their top-k results
        """
        results: Dict[str, List[Dict[str, Any]]] = {}
        for qi, query in enumerate(queries):
            sim_row = sims[qi]
            idxs = np.argsort(-sim_row)[:top_k]
            hits: List[Dict[str, Any]] = []
            for idx in idxs:
                hits.append({
                    'document': docs[idx],
                    'metadata': metas[idx],
                    'similarity': float(sim_row[idx])
                })
            results[query] = hits
        return results

    def _aggregate_hits(
        self,
        hits_by_chunk: Dict[str, List[Dict[str, Any]]],
        top_n: int
    ) -> List[Dict[str, Any]]:
        """
        Aggregate hits across different chunks
        :param hits_by_chunk: Dictionary mapping chunks to their hits
        :param top_n: Number of top results to return after aggregation

        :return: List of aggregated results, sorted by total similarity
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
                    entry = agg[doc]
                    entry['sum_similarity'] += sim
                    entry['count'] += 1
                    entry['chunks'].append(chunk)
        aggregated_list = sorted(
            agg.values(),
            key=lambda x: x['sum_similarity'],
            reverse=True
        )
        return aggregated_list[:top_n] if top_n is not None else aggregated_list

from typing import List, Dict, Any
import numpy as np
from loguru import logger
from core.embedder.embedding_processor import EmbeddingProcessor
from core.chroma_db.chroma_manager import ChromaDBManager

class EventSpecifics:
    """
    Класс для поиска специфик событий по эмбеддингам и агрегации результатов
    """
    def __init__(self, embedding_processor: EmbeddingProcessor, chroma_manager: ChromaDBManager):
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
        Ищет и агрегирует результаты для списка чанков текста
        """
        # 1. Загрузка содержимого коллекции
        contents = self._load_collection_contents(collection_name)
        if not contents:
            return []
        # 2. Нормализация эмбеддингов коллекции
        col_embs_norm = self.embedding_processor.normalize_embeddings(contents['embeddings'])
        # 3. Эмбеддинги запросов и их нормализация
        q_embs = self.embedding_processor.embed_texts(chunks)
        q_embs_norm = self.embedding_processor.normalize_embeddings(q_embs)
        # 4. Вычисление сходства
        sims = self.embedding_processor.compute_cosine_similarity(q_embs_norm, col_embs_norm)
        # 5. Сбор hit-ов по чанкам
        hits_by_chunk = self._get_topk_hits(
            sims,
            contents['documents'],
            contents['metadatas'],
            chunks,
            top_k
        )
        # 6. Агрегация результатов
        aggregated = self._aggregate_hits(hits_by_chunk, top_n)
        # 7. Возвращаем список документов
        return [item['document'] for item in aggregated]

    def _load_collection_contents(self, collection_name: str) -> Dict[str, Any]:
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

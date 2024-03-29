import tensorflow_hub as hub
from typing import List, Union, Dict, Any
import numpy as np
from sklearn.neighbors import NearestNeighbors
from transformers import BertTokenizer


class SemanticSearcher:
    def __init__(self, model_url: str = "https://tfhub.dev/tensorflow/bert_multi_cased_L-12_H-768_A-12/1",
                 tokenizer_model: str = 'bert-base-multilingual-cased',
                 n_neighbors: int = 5) -> None:
        self.texts = None
        self.nn = None
        self.embeddings = None
        self.embed = hub.load(model_url)
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_model)
        self.n_neighbors: int = n_neighbors
        self.fitted: bool = False
        self.texts: List[str]
        self.embeddings: np.ndarray

    def fit(self, texts: List[str], batch_size: int = 8) -> None:  # Batch size reduced due to mBERT memory demands (was 1k)
        self.embeddings = self.get_text_embedding(texts, batch_size)
        self.nn: NearestNeighbors = NearestNeighbors(n_neighbors=self.n_neighbors, metric="cosine")
        self.nn.fit(self.embeddings)
        self.texts: List[str] = texts
        self.fitted: bool = True

    def search(self, query_text: str, return_distance: bool = True) -> Union[List[Dict[str, Any]], List[str]]:
        if not self.fitted:
            raise ValueError("Fit the model with data before searching.")

        query_embedding = self.get_text_embedding([query_text])[0]
        distances, indices = self.nn.kneighbors([query_embedding])

        if return_distance:
            results: List[Dict[str, Any]] = [{'text': self.texts[idx], 'distance': dist} for idx, dist in
                                             zip(indices[0], distances[0])]
        else:
            results: List[str] = [self.texts[idx] for idx in indices[0]]

        return results

    def get_text_embedding(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
        all_embeddings: List[np.ndarray] = []
        for i in range(0, len(texts), batch_size):
            text_batch = texts[i: i + batch_size]
            encoded_input = self.tokenizer(text_batch, padding=True, truncation=True, return_tensors='tf')
            outputs = self.embed([
                encoded_input['input_ids'],
                encoded_input['attention_mask'],
                encoded_input['token_type_ids']
            ])
            emb_batch = outputs[0].numpy()
            all_embeddings.append(emb_batch)
        return np.vstack(all_embeddings)

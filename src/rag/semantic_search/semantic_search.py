from typing import List, Dict, Union
from sklearn.neighbors import NearestNeighbors
from langchain_openai import OpenAIEmbeddings


class SemanticSearcher:
    """
    A class to perform searches for semantically similar texts using OpenAI embeddings.
    """

    def __init__(self, openai_api_key: str, n_neighbors: int = 5):
        """
        Initializes the SemanticSearcher with an OpenAI API key and the number of neighbors.

        :param openai_api_key: API key for OpenAI.
        :param n_neighbors: Number of nearest neighbors to consider.
        """
        self.openai_api_key = openai_api_key
        self.texts: List[str] = []
        self.nn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.openai_embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key, model='text-embedding-3-large'
        )
        self.n_neighbors = n_neighbors
        self.fitted = False

    def fit(self, texts: List[str]) -> None:
        """
        Fits the NearestNeighbors model using embeddings of the provided texts.

        :param texts: A list of texts to fit the model on.
        :raises ValueError: If the texts list is empty.
        """
        if not texts:
            raise ValueError("The text list for fitting cannot be empty.")
        text_embeddings = self.openai_embeddings.embed_documents(texts)
        self.nn.fit(text_embeddings)
        self.texts = texts
        self.fitted = True

    def search(self, query_text: str, return_distance: bool = True) -> Union[List[Dict[str, Union[str, float]]], List[str]]:
        """
        Searches for semantically similar chunks of text based on a query string.

        :param query_text: The query string to search for.
        :param return_distance: Whether to return the distance metric with the search results.
        :return: If return_distance is true, returns a list of dictionaries
                 with text and their corresponding distances. Otherwise, returns only a list of texts.
        """
        if not self.fitted:
            raise ValueError("Cannot search before fit is called.")
        query_embedding = self.openai_embeddings.embed_documents([query_text])[0]
        distances, indices = self.nn.kneighbors([query_embedding])
        if return_distance:
            return [{'text': self.texts[idx], 'distance': dist} for idx, dist in zip(indices[0], distances[0])]
        else:
            return [self.texts[idx] for idx in indices[0]]

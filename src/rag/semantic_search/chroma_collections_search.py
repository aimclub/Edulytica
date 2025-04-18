import chromadb
import pandas as pd
import json
from copy import deepcopy


class ChromaSearcher:
    """
    A class to create ChromaDB collections from given specifics and to search in these collections.
    """

    COLLECTIONS_FILE = "all_collections.json"
    EMBEDDING_MODEL = "BAAI/bge-m3"

    def __init__(self, host, port):
        """
        Initialization of ChromaDB client. Requires host and port.
        """
        self.host = host
        self.port = port
        self.embedding_function = chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name=ChromaSearcher.EMBEDDING_MODEL)
        self.chroma_client = chromadb.HttpClient(host=self.host, port=self.port)
<<<<<<< HEAD
        t = []
        with open(ChromaSearcher.COLLECTIONS_FILE, "w", encoding='utf-8') as f:
            json.dump(t, f, ensure_ascii=False)
            f.close()

    def find_similar_records(self, collection_name, texts: list, n_results=5):
        """
        A method for searching parts of specifics that could be similar to a given text
        Arguments:
        - collection_name: str - A name of a collection where parts should be searched
        - texts: list - A lists of texts (str) to be found (compared)
        - n_results: int - Number of search results to return (by default 5)
        """
        collection = self.chroma_client.get_collection(collection_name, embedding_function=self.embedding_function)
        return collection.query(query_texts=texts, n_results=n_results, include=["documents", "metadatas"])

    def add_specific(self, file_name, sheet_name, collection_name):
        """
        A method for adding specific to ChromaDB collection
        Arguments:
        - file_name: str - A spreadsheet file with specific data.
        - sheet_name: str - Name of a sheet from spreadsheet file.
        - collection_name: str - Name of ChromaDB collection to be created. Must be Latin letters and numbers only.
        """
        spec_data = pd.read_excel(file_name, sheet_name=sheet_name, header=[0,1,2,3])
=======
        # self.chroma_client = chromadb.Client()
        self.openai_ef = chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(
            api_key=ChromaSearcher.OPENAI_API_KEY, model_name=ChromaSearcher.OPENAI_EMBEDDING_MODEL)

    def find_similar_records(self, collection_name, texts: list, n_results=5):
        # Поиск похожих записей в коллекции. Необходимо предоставить название коллекции collection_name и список искомых текстов texts
        # Дополнительно можно задать количество найденных записей. По умолчанию 5
        collection = self.chroma_client.get_collection(
            collection_name, embedding_function=self.openai_ef)
        return collection.query(
            query_texts=texts,
            n_results=n_results,
            include=[
                "documents",
                "metadatas"])

    def add_specific(self, file_name, sheet_name, collection_name):
        # Функция для добавления специфики из файла. Аргументы:
        # file_name - имя файла, в котором сохранена специфика (str).
        # sheet_name - название листа, в котором специфика сохранена (str).
        # collection_name - имя коллекции, в которой сохранить специфику конференции (str).
        spec_data = pd.read_excel(file_name, sheet_name=sheet_name, header=[0, 1, 2, 3])
>>>>>>> bc49c72f75a8532dc4d54298ba10635cf0e71c3e
        spec_data = spec_data.fillna("")
        res = {}
        res['description_full'] = []
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
        ids = []
        documents = []
        metadatas = []
        for j in range(len(res['description_full'])):
            ids.append("id" + str(j))
            documents.append(res['description_full'][j]['column_text'])
            md = {}
            md['column_title'] = res['description_full'][j]['column_title']
            metadatas.append(deepcopy(md))
        with open(ChromaSearcher.COLLECTIONS_FILE, "r", encoding='utf-8') as f:
            all_collections = json.load(f)
            f.close()
        all_collections.append({})
        all_collections[-1]['conf_title'] = spec_data.columns[0][0]
        all_collections[-1]['conf_title_short'] = sheet_name
        all_collections[-1]['collection_name'] = collection_name
<<<<<<< HEAD
        
        collection = self.chroma_client.create_collection(collection_name, embedding_function=self.embedding_function)
=======

        collection = self.chroma_client.create_collection(
            collection_name, embedding_function=self.openai_ef)
>>>>>>> bc49c72f75a8532dc4d54298ba10635cf0e71c3e
        collection.add(
            metadatas=metadatas,
            documents=documents,
            ids=ids
        )
        with open(ChromaSearcher.COLLECTIONS_FILE, "w", encoding='utf-8') as f:
            json.dump(all_collections, f, ensure_ascii=False)
            f.close()

    def get_specifics(self, collection_name):
<<<<<<< HEAD
        """
        A method to get collection contents by name
        Arguments:
        - collection_name: str - A name of ChromaDB collection (must be an existing collection)
        """
        collection = self.chroma_client.get_collection(collection_name, embedding_function=self.embedding_function)
        return collection.get(include=["documents", "embeddings", "metadatas"])
=======
        collection = self.chroma_client.get_collection(
            collection_name, embedding_function=self.openai_ef)
        return collection.get(include=["documents", "embeddings", "metadatas"])


DATA_FILE = ""  # path to Excel file with table

if __name__ == "__main__":
    cs = ChromaSearcher('localhost', 8000)
    cs.add_specific("Специфика редактированная.xlsx", "ППС", "PPS")
    cl = cs.get_specifics("PPS")
    cqq = cs.find_similar_records("PPS", ["Статья должна быть оформлена"])
    print(cl)
    print(cqq)
    cs.chroma_client.delete_collection("PPS")
>>>>>>> bc49c72f75a8532dc4d54298ba10635cf0e71c3e

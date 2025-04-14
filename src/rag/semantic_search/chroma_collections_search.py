import chromadb
import pandas as pd
import json
from copy import deepcopy

class ChromaSearcher:

    # CHROMA_HOST = "localhost"  # change
    # CHROMA_PORT = 8000
    COLLECTIONS_FILE = "all_collections.json"
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    OPENAI_API_KEY = "API_KEY"

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.chroma_client = chromadb.HttpClient(host=self.host, port=self.port)
        # self.chroma_client = chromadb.Client()
        self.openai_ef = chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(api_key=ChromaSearcher.OPENAI_API_KEY, model_name=ChromaSearcher.OPENAI_EMBEDDING_MODEL)

    def find_similar_records(self, collection_name, texts: list, n_results=5):
        # Поиск похожих записей в коллекции. Необходимо предоставить название коллекции collection_name и список искомых текстов texts
        # Дополнительно можно задать количество найденных записей. По умолчанию 5
        collection = self.chroma_client.get_collection(collection_name, embedding_function=self.openai_ef)
        return collection.query(query_texts=texts, n_results=n_results, include=["documents", "metadatas"])

    def add_specific(self, file_name, sheet_name, collection_name):
        # Функция для добавления специфики из файла. Аргументы:
        # file_name - имя файла, в котором сохранена специфика (str).
        # sheet_name - название листа, в котором специфика сохранена (str).
        # collection_name - имя коллекции, в которой сохранить специфику конференции (str).
        spec_data = pd.read_excel(file_name, sheet_name=sheet_name, header=[0,1,2,3])
        spec_data = spec_data.fillna("")
        res = {}
        res['description_full'] = []
        for i in spec_data.columns:
            ii = list(i)
            res['description_full'].append({})
            res['description_full'][-1]['column_title'] = ''
            for j in range(1, len(ii)):
                if not(ii[j].startswith("Unnamed")):
                    res['description_full'][-1]['column_title'] += ii[j]
                    res['description_full'][-1]['column_title'] += '__'
            res['description_full'][-1]['column_title'] = res['description_full'][-1]['column_title'][:-2]
            res['description_full'][-1]['column_text'] = " ".join(spec_data[i].tolist()).strip()
        ids = []
        documents = []
        metadatas = []
        for j in range(len(res['description_full'])):
            ids.append("id"+str(j))
            documents.append(res['description_full'][j]['column_text'])
            md = {}
            md['column_title'] = res['description_full'][j]['column_title']
            metadatas.append(deepcopy(md))
        with open(ChromaSearcher.COLLECTIONS_FILE, "r", encoding='utf-8') as f:
            all_collections = json.load(f)
        all_collections.append({})
        all_collections[-1]['conf_title'] = spec_data.columns[0][0]
        all_collections[-1]['conf_title_short'] = sheet_name
        all_collections[-1]['collection_name'] = collection_name
        
        collection = self.chroma_client.create_collection(collection_name, embedding_function=self.openai_ef)
        collection.add(
            metadatas=metadatas,
            documents=documents,
            ids=ids
        )
        with open(ChromaSearcher.COLLECTIONS_FILE, "w", encoding='utf-8') as f:
            json.dump(all_collections, f, ensure_ascii=False)


    def get_specifics(self, collection_name):
        collection = self.chroma_client.get_collection(collection_name, embedding_function=self.openai_ef)
        return collection.get(include=["documents", "embeddings", "metadatas"])

DATA_FILE = ""  # path to Excel file with table

if __name__ == "__main__":
    cs = ChromaSearcher('localhost', 8000)
    cs.add_specific("Специфика редактированная.xlsx","ППС","PPS")
    cl = cs.get_specifics("PPS")
    cqq = cs.find_similar_records("PPS", ["Статья должна быть оформлена"])
    print(cl)
    print(cqq)
    cs.chroma_client.delete_collection("PPS")
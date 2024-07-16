from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv('config/formatter.env')

class DocumentFormatter:
    """
    An auxiliary class containing methods for formatting json objects and splitting documents into chunks
    """

    @staticmethod
    def split(doc):
        """ split documents by chunks """
        loader = TextLoader(doc, encoding='utf-8')
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = int(getenv('CHUNK_SIZE')),
            chunk_overlap = int(getenv('CHUNK_OVERLAP')),
            length_function = len,
            is_separator_regex = False,
        )
        
        documents = text_splitter.split_documents(documents)

        return documents

    @staticmethod
    def deep_merge_json(json_list):
        """deep merge list json objects"""
        merged = {}

        for json_obj in json_list:
            merged = DocumentFormatter.merge_json(merged, json_obj)

        return merged

    @staticmethod
    def merge_json(json1, json2):
        """deep merge two json objects"""
        merged = json1.copy()

        for key, value in json2.items():
            key = key.lower()
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = DocumentFormatter.merge_json(merged[key], value)
            else:
                merged[key] = value

        return merged

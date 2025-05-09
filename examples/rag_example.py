import os
from dotenv import load_dotenv
from src.rag.utils.FileParser import FileParser
from src.rag.utils.TextProcessingUtils import TextProcessingUtils
from src.rag.semantic_search.SemanticSearcher import SemanticSearcher
from src.rag.llm.LanguageModelClient import LanguageModelClient
from src.rag.const import PROMPT_TEMPLATE


def ragExample():
    """
    Orchestrates the process of parsing text from a file, processing it,
    performing semantic search based on a user query, and generating a response.

    First, we load the API key for the model from .env, parse the document, perform preprocessing,
    perform a semantic search, send the result to llm and wait for an answer to the user's question.
    """

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")

    file_path = '../src/documents/doc.pdf'
    file_parser = FileParser(file_path)
    text_content = file_parser.parse()

    preprocessed_text = TextProcessingUtils.preprocess_text(text_content)
    chunks = TextProcessingUtils.text_to_chunks(preprocessed_text)

    searcher = SemanticSearcher(openai_api_key=openai_api_key, n_neighbors=5)
    searcher.fit(chunks)

    user_query = "Что может способствовать получению человеком достоверной информации о состоянии окружающей среды?"
    matches = searcher.search(user_query, return_distance=False)
    matches = '\n\n'.join(matches)

    prompt = PROMPT_TEMPLATE.format(matches=matches, user_query=user_query)

    llm_client = LanguageModelClient(api_key=openai_api_key)

    message = llm_client.get_answers_openai(
        prompt=prompt,
        model="gpt-3.5-turbo-instruct",
        max_tokens=2648,
        temperature=0.5)

    print(message)


if __name__ == "__main__":
    ragExample()

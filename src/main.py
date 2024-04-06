import os
from dotenv import load_dotenv
from parsing import parse_file
from preprocessing import preprocess_text, text_to_chunks
from semantic_search import SemanticSearcher
from litellm import completion


def main():
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")

    file_path = 'files/doc.pdf'
    text_content = parse_file(file_path)

    preprocessed_text = preprocess_text(text_content)
    chunks = text_to_chunks(preprocessed_text)

    searcher = SemanticSearcher(openai_api_key=openai_api_key, n_neighbors=5)
    searcher.fit(chunks)

    user_query = "В каких статьях Конституции РФ содержатся наиболее важные положения, связанные с экологической деятельностью государства?"
    matches = searcher.search(user_query, return_distance=False)
    matches = '\n\n'.join(matches)

    _prompt = f"""
    **Input:**
    {matches}

    **User Request:**
    {user_query}

    **Instructions:** You have received several chunks of text containing information that might be related to the 
    user's request concerning tanks. Your task is to analyze the text and extract relevant information to answer the 
    user's question. Make sure to base your response solely on the details present in the text. Do not add any 
    details, guess, or generate information beyond what is provided. If you cannot find the necessary information 
    within the provided text, respond with "Information not found." The answer must be given in the language that is 
    used in the context.

    Restrictions: Your response must strictly align with the information given in the text chunks. Avoid embellishing or 
    making assumptions if the text does not explicitly support them.
    """

    response = get_answers(prompt=_prompt, model="gpt-3.5-turbo-instruct", max_tokens=2648, temperature=0.5)

    if response:
        message = response['choices'][0]['message']['content']
        print(message)


def get_answers(prompt, model, max_tokens, temperature):
    response = completion(
        model=model,
        messages=[{"content": prompt, "role": "user"}],
        max_tokens=max_tokens,
        n=1,
        temperature=temperature
    )
    return response


if __name__ == "__main__":
    main()

from parsing import parse_file
from preprocessing import preprocess_text, text_to_chunks
from semantic_search import SemanticSearcher
from litellm import completion
from typing import List, Union, Dict, Any
from pprint import pprint
import os
import re


file_path = 'doc.pdf'
text_content = parse_file(file_path)

preprocessed_text = preprocess_text(text_content)
chunks = text_to_chunks(text=preprocessed_text)

searcher: SemanticSearcher = SemanticSearcher(n_neighbors=10)
searcher.fit(chunks)

user_query: str = ("В каких статьях Конституции РФ содержатся наиболее важные положения, связанные с экологической "
                   "деятельностью государства?")
matches = searcher.search(user_query, return_distance=False)
matches = '\n\n'.join(matches)

_prompt = f"""
Prompt for LLM:

**Input:**
{matches}

**User Request:**
{user_query}

**Instructions:** You have received several chunks of text containing information that might be related to the user's 
request concerning tanks. Your task is to analyze the text and extract relevant information to answer the user's 
question. Make sure to base your response solely on the details present in the text. Do not add any details, guess, 
or generate information beyond what is provided. If you cannot find the necessary information within the provided 
text, respond with "Information not found."

Restrictions: Your response must strictly align with the information given in the text chunks. Avoid embellishing or 
making assumptions if the text does not explicitly support them.
"""

print(_prompt)

os.environ["OPENAI_API_KEY"] = ""  # PUT YOUR TOKEN HERE

response = completion(
    model="gpt-4",
    messages=[{"content": _prompt, "role": "user"}],
    max_tokens=2048,
    n=1,
    temperature=1
)
message = response['choices'][0]['message']['content']
print(message)

"""response = completion(
    model="ollama/llama2",
    messages=[{"content": _prompt, "role": "user"}],
    api_base="http://localhost:11434"
)
output = ""
for chunk in response:
    print(chunk)"""
    #output += str(chunk['choices'][0]['delta']["content"])

#matches = re.findall(r'"([^"]*)"', output)

#text_inside_quotes = matches[0]
#print(text_inside_quotes)



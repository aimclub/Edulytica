# RAG

---
Package for an experiment with semantic search, kNN and the mBERT model are used. 
RecursiveCharacterTextSplitter from langchain is used for chunking. In the file main.py there is text processing and
a request to LLM via litellm (currently OpenAI).

---
## Structure:
- **LanguageModelClient** - A class for working with various models. It works through *litellm*, is currently configured
for ChatGPT, if you install a different model, you may have to change the code a little to get the response text,
because there is no single response;
- **SemanticSearcher** - A class for semantic search. The kNN algorithm is used: chunks of the entire text and the 
user's query are taken, then the "distance" is determined, then it returns the 5 closest chunks that the model will 
already process to answer the user's question;
- **utils** - The directory contains a class for parsing different documents and a class for preprocessing text 
(removing unnecessary characters, tables, etc., chunking);
- **const.py** - At the moment, there is just a prompt in which the user's query and the result of the semantic 
search will be added through the filter.
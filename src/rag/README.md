# RAG (Retrieval-Augmented Generation)

---
Package for an experiment with semantic search, kNN and the mBERT model are used. 
RecursiveCharacterTextSplitter from langchain is used for chunking. In the file main.py there is text processing and
a request to LLM via litellm (currently OpenAI).

---
## System Architecture

![RAG Sequence Diagram](docs/rag_sequnce.png)

## System Components

The RAG system consists of the following main components:

1. **Fast API** - Entry point to the system, provides a REST API for receiving prompt enrichment requests.

2. **Text Processor** - Responsible for processing input text, extracting keywords, and preparing embeddings.

3. **Event Specifics** - Finds specifics for the text, matching the request with a particular event type.

4. **Chroma DB** - Vector database for storing and retrieving information about events.

5. **Prompt Enricher** - Enriches the original prompt with additional event-specific information.

## Data Flow

1. The user sends an enrichment request via Fast API
2. Text Processor processes the text, extracts keywords, and creates embeddings
3. Event Specifics analyzes the text and finds appropriate specifications for it
4. Chroma DB extracts suitable event specifics from the vector storage
5. Prompt Enricher enhances the original prompt with event-specific information
6. The enriched prompt is returned to the user

---
## Previous Structure:
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
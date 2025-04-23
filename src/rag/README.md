# RAG (Retrieval-Augmented Generation)

---
Package for enhancing prompts with contextual information (Retrieval-Augmented Generation) within the Edulytica project.

---
<<<<<<< HEAD
## Table of Contents
- [System Architecture](#system-architecture)


- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Supported Conferences](#supported-conferences)
- [Adding Data to ChromaDB](#adding-data-to-chromadb)

## System Architecture

![RAG Sequence Diagram](docs/rag_sequnce.png)

## Project Structure

```
src/rag/
├── api/                  # API interfaces for accessing the RAG system
├── config/               # Configuration files
│   └── config.yaml       # Main configuration file
├── core/                 # Core components
│   ├── chroma_db/        # ChromaDB interaction
│   ├── embedder/         # Creation and processing of embeddings
│   ├── event_specifics/  # Event specifics search
│   ├── prompt_enricher/  # Prompt enrichment with context
│   ├── text_processor/   # Text processing
│   └── utils/            # Utilities
├── data/                 # System data
│   └── Specification.xlsx # Conference specifications
├── docs/                 # Documentation
├── docker-compose.yml    # Docker configuration
├── pipeline.py           # Main RAG pipeline
└── requirements.txt      # Project dependencies
```

## Installation

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Running with Docker

```bash
docker-compose up -d
```

## Usage

Example of using the RAG pipeline:

```python
from pipeline import RAGPipeline

# Initialize the RAG pipeline
pipeline = RAGPipeline()

# Load article text
with open("path/to/article.txt", "r", encoding="utf-8") as f:
    article_text = f.read()

# Specify the conference
conference_name = "KMU"

# Basic prompt for processing
prompt = """
You are an expert, experienced reviewer of scientific papers.
Analyze the provided scientific article and identify its title.
"""

# Enrich the prompt with contextual information about the conference
enriched_prompt = pipeline.pipeline(article_text, conference_name, prompt)

# Display the result
print(enriched_prompt)
```

### Main Components

- **RAGPipeline**: Central component that integrates all modules
- **EmbeddingProcessor**: Creates embeddings
- **ChromaDBManager**: Manages the ChromaDB database 
- **EventSpecifics**: Searches for specific information about events (conferences)
- **PromptEnricher**: Enriches prompts with contextual information
- **TextProcessor**: Processes and splits text into parts for analysis

## Configuration

The system is configured through the `config.yaml` file in the `config` directory:

```yaml
# ChromaDB connection settings
host: localhost
port: 8080
collections_file: all_collections.json

# Embedding model to use
embedding_model: BAAI/bge-m3

# RAG settings
rag_promt: "общая информация о конференции, правила оформления статей, требования к структуре и форматированию, цели конференции"
additional_info_prefix: "Дополнительная информация:"

# Number of top results to retrieve
general_top: 3
artical_top: 1
```

## Supported Conferences

The system currently supports 5 types of conferences:

1. **PPS** ;
2. **KMU**;
3. **EPI**;
4. **YSC**;
5. **FRUCT**.


## Adding Data to ChromaDB

To add conference data from Excel files to ChromaDB, use the `ChromaDBManager` class:

```python
from core.chroma_db.chroma_manager import ChromaDBManager
from core.embedder.embedding_processor import EmbeddingProcessor

# Initialize components
embedding_processor = EmbeddingProcessor()
chroma_manager = ChromaDBManager(embedding_processor=embedding_processor)

# Path to the Excel file with conference specifications
specifics_path = "data/Specification.xlsx"

# Add data from Excel sheets to ChromaDB collections
# Parameters: file_path, sheet_name, collection_name
chroma_manager.add_from_excel(specifics_path, "ППС", "PPS")
chroma_manager.add_from_excel(specifics_path, "КМУ", "KMU")
chroma_manager.add_from_excel(specifics_path, "ЭПИ", "EPI")
chroma_manager.add_from_excel(specifics_path, "YSC", "YSC")
chroma_manager.add_from_excel(specifics_path, "FRUCT", "FRUCT")
```


=======
## Structure:
- **LanguageModelClient** - A class for working with various models. It works through *litellm*, is currently configured
for ChatGPT, if you install a different model, you may have to change the code a little to get the response text,
because there is no single response;
- **SemanticSearcher** - A class for semantic search. The kNN algorithm is used: chunks of the entire text and the 
user's query are taken, then the "distance" is determined, then it returns the 5 closest chunks that the model will 
already process to answer the user's question;
- **ChromaSearcher** - A class to work with ChromaDB server. Designed to store conference descriptions, retrieve 
previously added descriptions and decription parts similar to users's query (5 by default). 
Uses BAAI/bge-m3 to calculate text embeddings;
- **utils** - The directory contains a class for parsing different documents and a class for preprocessing text 
(removing unnecessary characters, tables, etc., chunking);
- **const.py** - At the moment, there is just a prompt in which the user's query and the result of the semantic 
search will be added through the filter.
>>>>>>> 7f6b7c64966a9d878fd03dbe376627772d86d8ef

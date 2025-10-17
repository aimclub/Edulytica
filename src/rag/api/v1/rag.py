"""
Description
    RAG API exposing endpoints to ingest text into a vector store and to run
    retrieval-augmented generation over an input text with a prompt.

Routes:
    POST /upload_text  — Ingest text: chunk, ensure collection, and add documents.
    POST /get_result   — Run the RAG pipeline and return the generated result.
"""

from fastapi import APIRouter, Body
from starlette.status import HTTP_200_OK

from src.common.utils.logger import api_logs
from src.rag import RAGPipeline


rag_v1 = APIRouter(prefix="/api/rag/v1", tags=['rag'])
pipeline = RAGPipeline()


@api_logs(rag_v1.post('/upload_text', status_code=HTTP_200_OK), exclude_args=['text'])
async def upload_text_handler(
        text: str = Body(...),
        event_name: str = Body(...)
):
    """
    Description
        Ingest a text into the vector store under the given event name:
        - Preprocess text into chunks,
        - Ensure the collection exists,
        - Add documents to the collection.

    Args:
        text (str): Source text to index.
        event_name (str): Logical collection name (one collection per event).

    Responses:
        200: {"status": "success" | "failed", "chunks_uploaded": <int>}

    Raises:
        HTTPException: On unexpected failures at preprocessing or storage layers.
    """
    chunks = pipeline.preprocess_article(text)
    pipeline.chroma_manager.create_collection(event_name)
    success = pipeline.chroma_manager.add_documents(
        collection_name=event_name,
        documents=chunks,
    )
    return {"status": "success" if success else "failed", "chunks_uploaded": len(chunks)}


@api_logs(rag_v1.post('/get_result', status_code=HTTP_200_OK), exclude_args=['text', 'prompt'])
async def get_result_handler(
        text: str = Body(...),
        event_name: str = Body(...),
        prompt: str = Body(...)
):
    """
    Description
        Run the RAG pipeline over the provided text and prompt, returning
        the generated result.

    Args:
        text (str): Source document text.
        event_name (str): Collection/event name used for retrieval.
        prompt (str): Original prompt for LLM's.

    Responses:
        200: {"result": "<string with generated output>"}

    Raises:
        HTTPException: On unexpected failures during retrieval or generation.
    """
    result = pipeline.pipeline(
        article_text=text,
        conference_name=event_name,
        prompt=prompt
    )
    return {"result": result}

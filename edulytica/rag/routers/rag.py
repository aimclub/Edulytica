from fastapi import APIRouter, Body
from edulytica.common.utils.logger import api_logs
from edulytica.rag import RAGPipeline


rag_router = APIRouter(prefix="/rag")
pipeline = RAGPipeline()


@api_logs(rag_router.post('/upload_text'))
async def upload_text_handler(
        text: str = Body(...),
        event_name: str = Body(...)
):
    chunks = pipeline.preprocess_article(text)
    pipeline.chroma_manager.create_collection(event_name)
    success = pipeline.chroma_manager.add_documents(
        collection_name=event_name,
        documents=chunks,
    )
    return {"status": "success" if success else "failed", "chunks_uploaded": len(chunks)}


@api_logs(rag_router.post('/get_result'))
async def get_result_handler(
        text: str = Body(...),
        event_name: str = Body(...),
        prompt: str = Body(...)
):
    result = pipeline.pipeline(
        article_text=text,
        conference_name=event_name,
        prompt=prompt
    )
    return {"result": result}

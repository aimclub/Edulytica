from fastapi import HTTPException, Depends, APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from src.edulytica_api.auth.auth_bearer import access_token_auth
from src.edulytica_api.crud.model_crud import ModelCrud
from src.edulytica_api.database import get_session
from src.edulytica_api.llms.llm_wrapper import Models, LLMWrapper

llm_rt = APIRouter(prefix='/llm_predict')


@llm_rt.post("/predict")
async def predict(
        prompt: str = Body(..., embed=True),
        model: Models = Body(...),
        parameters: dict = Body(None),
        auth_data: dict = Depends(access_token_auth)
):
    try:
        llm_sdk = LLMWrapper(model=model)
        llm_response = llm_sdk.send_request(prompt, **parameters)
        generated_text = llm_sdk.process_response(llm_response)
        return {"response": generated_text}
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@llm_rt.get("/ping")
async def ping():
    return {"status": "pong", "router": "llm_router"}


@llm_rt.get("/stats")
async def stats(
        model_tag: str = Body(..., embed=True),
        auth_data: dict = Depends(access_token_auth),
        session: AsyncSession = Depends(get_session)
):
    model_stats = await ModelCrud.get_model_statistics_by_tag(
        model_tag=model_tag, session=session)

    if not model_stats:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Wrong model tag")

    return {
        "status": HTTP_200_OK,
        **model_stats
    }

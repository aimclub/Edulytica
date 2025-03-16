from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.updated_models import Document
from src.edulytica_api.schemas import DocumentModels


class DocumentCrud(

    BaseCrudFactory(
        model=Document,
        update_schema=DocumentModels.Update,
        create_schema=DocumentModels.Create,
        get_schema=DocumentModels.Get,
    )
):
    pass

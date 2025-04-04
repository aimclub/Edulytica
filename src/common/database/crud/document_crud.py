from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import Document
from src.common.database.schemas import DocumentModels


class DocumentCrud(

    BaseCrudFactory(
        model=Document,
        update_schema=DocumentModels.Update,
        create_schema=DocumentModels.Create,
        get_schema=DocumentModels.Get,
    )
):
    pass

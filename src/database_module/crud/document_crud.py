from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import Document
from src.database_module.schemas import DocumentModels


class DocumentCrud(

    BaseCrudFactory(
        model=Document,
        update_schema=DocumentModels.Update,
        create_schema=DocumentModels.Create,
        get_schema=DocumentModels.Get,
    )
):
    pass

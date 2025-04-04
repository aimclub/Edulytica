from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import DocumentSummary
from src.database_module.schemas import DocumentSummaryModels


class DocumentSummaryCrud(

    BaseCrudFactory(
        model=DocumentSummary,
        update_schema=DocumentSummaryModels.Update,
        create_schema=DocumentSummaryModels.Create,
        get_schema=DocumentSummaryModels.Get,
    )
):
    pass

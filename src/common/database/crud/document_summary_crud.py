from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import DocumentSummary
from src.common.database.schemas import DocumentSummaryModels


class DocumentSummaryCrud(

    BaseCrudFactory(
        model=DocumentSummary,
        update_schema=DocumentSummaryModels.Update,
        create_schema=DocumentSummaryModels.Create,
        get_schema=DocumentSummaryModels.Get,
    )
):
    pass

from src.edulytica_api.crud.base.factory import BaseCrudFactory
from src.edulytica_api.models import DocumentSummary
from src.edulytica_api.schemas import DocumentSummaryModels


class DocumentSummaryCrud(

    BaseCrudFactory(
        model=DocumentSummary,
        update_schema=DocumentSummaryModels.Update,
        create_schema=DocumentSummaryModels.Create,
        get_schema=DocumentSummaryModels.Get,
    )
):
    pass

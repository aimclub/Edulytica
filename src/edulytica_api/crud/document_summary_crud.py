from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.updated_models import DocumentSummary
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

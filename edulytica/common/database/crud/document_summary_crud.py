from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import DocumentSummary
from edulytica.common.database.schemas import DocumentSummaryModels


class DocumentSummaryCrud(

    BaseCrudFactory(
        model=DocumentSummary,
        update_schema=DocumentSummaryModels.Update,
        create_schema=DocumentSummaryModels.Create,
        get_schema=DocumentSummaryModels.Get,
    )
):
    pass

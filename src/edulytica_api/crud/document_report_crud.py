from src.edulytica_api.crud.base.factory import BaseCrudFactory
from src.edulytica_api.models import DocumentReport
from src.edulytica_api.schemas import DocumentReportModels


class DocumentReportCrud(

    BaseCrudFactory(
        model=DocumentReport,
        update_schema=DocumentReportModels.Update,
        create_schema=DocumentReportModels.Create,
        get_schema=DocumentReportModels.Get,
    )
):
    pass

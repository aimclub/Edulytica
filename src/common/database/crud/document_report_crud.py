from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import DocumentReport
from src.common.database.schemas import DocumentReportModels


class DocumentReportCrud(

    BaseCrudFactory(
        model=DocumentReport,
        update_schema=DocumentReportModels.Update,
        create_schema=DocumentReportModels.Create,
        get_schema=DocumentReportModels.Get,
    )
):
    pass

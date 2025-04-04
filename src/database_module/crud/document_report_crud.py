from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import DocumentReport
from src.database_module.schemas import DocumentReportModels


class DocumentReportCrud(

    BaseCrudFactory(
        model=DocumentReport,
        update_schema=DocumentReportModels.Update,
        create_schema=DocumentReportModels.Create,
        get_schema=DocumentReportModels.Get,
    )
):
    pass

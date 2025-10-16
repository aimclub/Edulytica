from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import DocumentReport
from src.common.database.schemas.system_schemas import DocumentReportGet, DocumentReportCreate, DocumentReportUpdate


class DocumentReportCrud(
    GenericCrud[DocumentReport, DocumentReportGet, DocumentReportCreate, DocumentReportUpdate]
):
    base_model = DocumentReport
    get_schema = DocumentReportGet
    create_schema = DocumentReportCreate
    update_schema = DocumentReportUpdate

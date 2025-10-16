from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import DocumentSummary
from src.common.database.schemas.system_schemas import DocumentSummaryGet, DocumentSummaryCreate, DocumentSummaryUpdate


class DocumentSummaryCrud(
    GenericCrud[DocumentSummary, DocumentSummaryGet, DocumentSummaryCreate, DocumentSummaryUpdate]
):
    base_model = DocumentSummary
    get_schema = DocumentSummaryGet
    create_schema = DocumentSummaryCreate
    update_schema = DocumentSummaryUpdate

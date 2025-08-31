from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import Document
from src.common.database.schemas.system_schemas import DocumentGet, DocumentCreate, DocumentUpdate


class DocumentCrud(
    GenericCrud[Document, DocumentGet, DocumentCreate, DocumentUpdate]
):
    base_model = Document
    get_schema = DocumentGet
    create_schema = DocumentCreate
    update_schema = DocumentUpdate

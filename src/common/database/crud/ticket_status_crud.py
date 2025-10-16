from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import TicketStatus
from src.common.database.schemas.system_schemas import TicketStatusGet, TicketStatusCreate, TicketStatusUpdate


class TicketStatusCrud(
    GenericCrud[TicketStatus, TicketStatusGet, TicketStatusCreate, TicketStatusUpdate]
):
    base_model = TicketStatus
    get_schema = TicketStatusGet
    create_schema = TicketStatusCreate
    update_schema = TicketStatusUpdate

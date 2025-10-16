from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import TicketType
from src.common.database.schemas.system_schemas import TicketTypeGet, TicketTypeCreate, TicketTypeUpdate


class TicketTypeCrud(
    GenericCrud[TicketType, TicketTypeGet, TicketTypeCreate, TicketTypeUpdate]
):
    base_model = TicketType
    get_schema = TicketTypeGet
    create_schema = TicketTypeCreate
    update_schema = TicketTypeUpdate

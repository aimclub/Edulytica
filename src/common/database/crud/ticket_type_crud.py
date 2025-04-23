from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import TicketType
from src.common.database.schemas import TicketTypeModels


class TicketTypeCrud(

    BaseCrudFactory(
        model=TicketType,
        update_schema=TicketTypeModels.Update,
        create_schema=TicketTypeModels.Create,
        get_schema=TicketTypeModels.Get,
    )
):
    pass

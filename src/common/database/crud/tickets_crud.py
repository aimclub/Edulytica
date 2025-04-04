from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import Ticket
from src.common.database.schemas import TicketModels


class TicketCrud(

    BaseCrudFactory(
        model=Ticket,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

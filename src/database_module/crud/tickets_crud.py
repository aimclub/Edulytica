from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import Ticket
from src.database_module.schemas import TicketModels


class TicketCrud(

    BaseCrudFactory(
        model=Ticket,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.updated_models import Ticket
from src.edulytica_api.schemas import TicketModels


class TicketCrud(

    BaseCrudFactory(
        model=Ticket,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

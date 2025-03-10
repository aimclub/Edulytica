from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.models import Tickets
from src.edulytica_api.schemas import TicketModels


class TicketsCrud(
    BaseCrudFactory(
        model=Tickets,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

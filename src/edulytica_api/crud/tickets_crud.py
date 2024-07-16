from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.models import Tickets
from src.edulytica_api.schemas.llm_schema import TicketsUpdate, \
    TicketsCreate, TicketsGet


class TicketsCrud(

    BaseCrudFactory(
        model=Tickets,
        update_schema=TicketsUpdate,
        create_schema=TicketsCreate,
        get_schema=TicketsGet,
    )
):
    pass

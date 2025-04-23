from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import TicketStatus
from src.common.database.schemas import TicketStatusModels


class TicketStatusCrud(

    BaseCrudFactory(
        model=TicketStatus,
        update_schema=TicketStatusModels.Update,
        create_schema=TicketStatusModels.Create,
        get_schema=TicketStatusModels.Get,
    )
):
    pass

from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import TicketStatus
from edulytica.common.database.schemas import TicketStatusModels


class TicketStatusCrud(

    BaseCrudFactory(
        model=TicketStatus,
        update_schema=TicketStatusModels.Update,
        create_schema=TicketStatusModels.Create,
        get_schema=TicketStatusModels.Get,
    )
):
    pass

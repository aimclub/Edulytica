from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import TicketType
from edulytica.common.database.schemas import TicketTypeModels


class TicketTypeCrud(

    BaseCrudFactory(
        model=TicketType,
        update_schema=TicketTypeModels.Update,
        create_schema=TicketTypeModels.Create,
        get_schema=TicketTypeModels.Get,
    )
):
    pass

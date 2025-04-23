from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import UserRole
from src.common.database.schemas import TicketModels


class TicketStatusCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

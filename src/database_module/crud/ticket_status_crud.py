from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import UserRole
from src.database_module.schemas import TicketModels


class TicketStatusCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.updated_models import UserRole
from src.edulytica_api.schemas import TicketModels


class TicketStatusCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    pass

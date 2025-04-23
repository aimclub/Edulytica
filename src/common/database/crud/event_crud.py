from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import Event
from src.common.database.schemas import EventModels


class EventCrud(

    BaseCrudFactory(
        model=Event,
        update_schema=EventModels.Update,
        create_schema=EventModels.Create,
        get_schema=EventModels.Get,
    )
):
    pass

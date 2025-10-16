from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import Event
from src.common.database.schemas.system_schemas import EventGet, EventCreate, EventUpdate


class EventCrud(
    GenericCrud[Event, EventGet, EventCreate, EventUpdate]
):
    base_model = Event
    get_schema = EventGet
    create_schema = EventCreate
    update_schema = EventUpdate

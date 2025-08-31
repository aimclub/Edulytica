from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import CustomEvent
from src.common.database.schemas.system_schemas import CustomEventGet, CustomEventCreate, CustomEventUpdate


class CustomEventCrud(
    GenericCrud[CustomEvent, CustomEventGet, CustomEventCreate, CustomEventUpdate]
):
    base_model = CustomEvent
    get_schema = CustomEventGet
    create_schema = CustomEventCreate
    update_schema = CustomEventUpdate

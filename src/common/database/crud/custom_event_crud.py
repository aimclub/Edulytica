from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import CustomEvent
from src.common.database.schemas import CustomEventModels


class CustomEventCrud(

    BaseCrudFactory(
        model=CustomEvent,
        update_schema=CustomEventModels.Update,
        create_schema=CustomEventModels.Create,
        get_schema=CustomEventModels.Get,
    )
):
    pass

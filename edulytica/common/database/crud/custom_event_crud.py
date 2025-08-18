from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import CustomEvent
from edulytica.common.database.schemas import CustomEventModels


class CustomEventCrud(

    BaseCrudFactory(
        model=CustomEvent,
        update_schema=CustomEventModels.Update,
        create_schema=CustomEventModels.Create,
        get_schema=CustomEventModels.Get,
    )
):
    pass

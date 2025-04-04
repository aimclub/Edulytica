from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import User
from src.common.database.schemas import UserModels


class UserCrud(
    BaseCrudFactory(
        model=User,
        update_schema=UserModels.Update,
        create_schema=UserModels.Create,
        get_schema=UserModels.Get,
    )
):
    pass

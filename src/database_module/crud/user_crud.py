from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import User
from src.database_module.schemas import UserModels


class UserCrud(
    BaseCrudFactory(
        model=User,
        update_schema=UserModels.Update,
        create_schema=UserModels.Create,
        get_schema=UserModels.Get,
    )
):
    pass

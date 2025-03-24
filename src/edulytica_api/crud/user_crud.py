from src.edulytica_api.crud.base.factory import BaseCrudFactory
from src.edulytica_api.models import User
from src.edulytica_api.schemas import UserModels


class UserCrud(
    BaseCrudFactory(
        model=User,
        update_schema=UserModels.Update,
        create_schema=UserModels.Create,
        get_schema=UserModels.Get,
    )
):
    pass

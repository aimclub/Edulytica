from src.edulytica_api.crud.factory import CrudFactory, BaseCrudFactory
from src.edulytica_api.models.models import User
from src.edulytica_api.schemas.auth import UserUpdate, UserCreate, UserGet


class UserCrud(
    BaseCrudFactory(
        model=User,
        update_schema=UserUpdate,
        create_schema=UserCreate,
        get_schema=UserGet,
    )
):
    pass
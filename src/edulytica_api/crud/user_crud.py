from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.auth import User
from src.edulytica_api.schemas.auth import UserUpdate, UserCreate, UserGet


class UserCrud(
    BaseCrudFactory(
        User,
        UserUpdate,
        UserCreate,
        UserGet,
    )
):
    pass
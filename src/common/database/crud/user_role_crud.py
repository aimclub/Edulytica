from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import UserRole
from src.common.database.schemas import UserRoleModels


class UserRoleCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=UserRoleModels.Update,
        create_schema=UserRoleModels.Create,
        get_schema=UserRoleModels.Get,
    )
):
    pass

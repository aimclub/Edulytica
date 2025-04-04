from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import UserRole
from src.database_module.schemas import UserRoleModels


class UserRoleCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=UserRoleModels.Update,
        create_schema=UserRoleModels.Create,
        get_schema=UserRoleModels.Get,
    )
):
    pass

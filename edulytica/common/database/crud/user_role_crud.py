from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import UserRole
from edulytica.common.database.schemas import UserRoleModels


class UserRoleCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=UserRoleModels.Update,
        create_schema=UserRoleModels.Create,
        get_schema=UserRoleModels.Get,
    )
):
    pass

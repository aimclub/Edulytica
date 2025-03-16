from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.updated_models import UserRole
from src.edulytica_api.schemas import UserRoleModels


class UserRoleCrud(

    BaseCrudFactory(
        model=UserRole,
        update_schema=UserRoleModels.Update,
        create_schema=UserRoleModels.Create,
        get_schema=UserRoleModels.Get,
    )
):
    pass

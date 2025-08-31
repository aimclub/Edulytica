from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import UserRole
from src.common.database.schemas.system_schemas import UserRoleGet, UserRoleCreate, UserRoleUpdate


class UserRoleCrud(
    GenericCrud[UserRole, UserRoleGet, UserRoleCreate, UserRoleUpdate]
):
    base_model = UserRole
    get_schema = UserRoleGet
    create_schema = UserRoleCreate
    update_schema = UserRoleUpdate

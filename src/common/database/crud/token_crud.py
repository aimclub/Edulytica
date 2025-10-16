from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import Token
from src.common.database.schemas.system_schemas import TokenGet, TokenCreate, TokenUpdate


class TokenCrud(
    GenericCrud[Token, TokenGet, TokenCreate, TokenUpdate]
):
    base_model = Token
    get_schema = TokenGet
    create_schema = TokenCreate
    update_schema = TokenUpdate

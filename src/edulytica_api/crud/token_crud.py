from src.edulytica_api.crud.factory import CrudFactory, BaseCrudFactory
from src.edulytica_api.models.auth import Token
from src.edulytica_api.schemas.auth import TokenUpdate, TokenCreate, TokenGet


class TokenCrud(

    BaseCrudFactory(
        model=Token,
        update_schema=TokenUpdate,
        create_schema=TokenCreate,
        get_schema=TokenGet,
    )
):
    pass
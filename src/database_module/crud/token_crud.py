from src.database_module.crud.base.factory import BaseCrudFactory
from src.database_module.models import Token
from src.database_module.schemas import TokenModels


class TokenCrud(

    BaseCrudFactory(
        model=Token,
        update_schema=TokenModels.Update,
        create_schema=TokenModels.Create,
        get_schema=TokenModels.Get,
    )
):
    pass

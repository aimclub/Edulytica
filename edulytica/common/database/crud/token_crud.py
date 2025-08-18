from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import Token
from edulytica.common.database.schemas import TokenModels


class TokenCrud(

    BaseCrudFactory(
        model=Token,
        update_schema=TokenModels.Update,
        create_schema=TokenModels.Create,
        get_schema=TokenModels.Get,
    )
):
    pass

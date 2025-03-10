from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.models import Token
from src.edulytica_api.schemas import TokenModels


class TokenCrud(
    BaseCrudFactory(
        model=Token,
        update_schema=TokenModels.Update,
        create_schema=TokenModels.Create,
        get_schema=TokenModels.Get,
    )
):
    pass

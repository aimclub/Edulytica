from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.models import ResultFiles
from src.edulytica_api.schemas.llm_schema import ResultFilesUpdate, ResultFilesGet, ResultFilesCreate


class ResultFilesCrud(

    BaseCrudFactory(
        model=ResultFiles,
        update_schema=ResultFilesUpdate,
        create_schema=ResultFilesCreate,
        get_schema=ResultFilesGet,
    )
):
    pass
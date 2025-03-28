from src.edulytica_api.crud.factory import BaseCrudFactory
from src.edulytica_api.models.models import ResultFiles
from src.edulytica_api.schemas import ResultFilesModels


class ResultFilesCrud(

    BaseCrudFactory(
        model=ResultFiles,
        update_schema=ResultFilesModels.Update,
        create_schema=ResultFilesModels.Create,
        get_schema=ResultFilesModels.Get,
    )
):
    pass

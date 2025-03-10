from src.edulytica_api.schemas.system_schemas import (
    _UserCreate,
    _UserUpdate,
    _UserGet,
    _TokenCreate,
    _TokenUpdate,
    _TokenGet,
    _TicketsCreate,
    _TicketsUpdate,
    _TicketsGet,
    _ResultFilesCreate,
    _ResultFilesUpdate,
    _ResultFilesGet,
)


class UserModels:
    class Create(_UserCreate):
        pass

    class Update(_UserUpdate):
        pass

    class Get(_UserGet):
        pass


class TokenModels:
    class Create(_TokenCreate):
        pass

    class Update(_TokenUpdate):
        pass

    class Get(_TokenGet):
        pass


class TicketModels:
    class Create(_TicketsCreate):
        pass

    class Update(_TicketsUpdate):
        pass

    class Get(_TicketsGet):
        pass


class ResultFilesModels:
    class Create(_ResultFilesCreate):
        pass

    class Update(_ResultFilesUpdate):
        pass

    class Get(_ResultFilesGet):
        pass

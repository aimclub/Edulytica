from src.edulytica_api.schemas.system_schemas import (
    _UserCreate,
    _UserUpdate,
    _UserGet,
    _TokenCreate,
    _TokenUpdate,
    _TokenGet,
    _UserRoleCreate,
    _UserRoleUpdate,
    _UserRoleGet,
    _CheckCodeCreate,
    _CheckCodeUpdate,
    _CheckCodeGet,
    _TicketCreate,
    _TicketUpdate,
    _TicketGet,
    _TicketStatusCreate,
    _TicketStatusUpdate,
    _TicketStatusGet,
    _DocumentCreate,
    _DocumentUpdate,
    _DocumentGet,
    _DocumentSummaryCreate,
    _DocumentSummaryUpdate,
    _DocumentSummaryGet,
    _DocumentReportCreate,
    _DocumentReportUpdate,
    _DocumentReportGet,
    _EventCreate,
    _EventUpdate,
    _EventGet,
    _CustomEventCreate,
    _CustomEventUpdate,
    _CustomEventGet)


class UserModels:
    class Create(_UserCreate):
        pass

    class Update(_UserUpdate):
        pass

    class Get(_UserGet):
        pass


class UserRoleModels:
    class Create(_UserRoleCreate):
        pass

    class Update(_UserRoleUpdate):
        pass

    class Get(_UserRoleGet):
        pass


class CheckCodeModels:
    class Create(_CheckCodeCreate):
        pass

    class Update(_CheckCodeUpdate):
        pass

    class Get(_CheckCodeGet):
        pass


class TicketStatusModels:
    class Create(_TicketCreate):
        pass

    class Update(_TicketUpdate):
        pass

    class Get(_TicketGet):
        pass


class TicketModels:
    class Create(_TicketStatusCreate):
        pass

    class Update(_TicketStatusUpdate):
        pass

    class Get(_TicketStatusGet):
        pass


class DocumentModels:
    class Create(_DocumentCreate):
        pass

    class Update(_DocumentUpdate):
        pass

    class Get(_DocumentGet):
        pass


class DocumentSummaryModels:
    class Create(_DocumentSummaryCreate):
        pass

    class Update(_DocumentSummaryUpdate):
        pass

    class Get(_DocumentSummaryGet):
        pass


class DocumentReportModels:
    class Create(_DocumentReportCreate):
        pass

    class Update(_DocumentReportUpdate):
        pass

    class Get(_DocumentReportGet):
        pass


class TokenModels:
    class Create(_TokenCreate):
        pass

    class Update(_TokenUpdate):
        pass

    class Get(_TokenGet):
        pass


class EventModels:
    class Create(_EventCreate):
        pass

    class Update(_EventUpdate):
        pass

    class Get(_EventGet):
        pass


class CustomEventModels:
    class Create(_CustomEventCreate):
        pass

    class Update(_CustomEventUpdate):
        pass

    class Get(_CustomEventGet):
        pass

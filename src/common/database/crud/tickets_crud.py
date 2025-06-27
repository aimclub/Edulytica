"""
This module defines a specialized CRUD class for managing ticket-related operations.

Classes:
    TicketCrud: Extends the generic CRUD factory with additional logic
                to retrieve tickets by ID, including shared ones.
"""

import uuid
from typing import Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.crud.custom_event_crud import CustomEventCrud
from src.common.database.crud.event_crud import EventCrud
from src.common.database.models import Ticket
from src.common.database.schemas import TicketModels


class TicketCrud(
    BaseCrudFactory(
        model=Ticket,
        update_schema=TicketModels.Update,
        create_schema=TicketModels.Create,
        get_schema=TicketModels.Get,
    )
):
    @staticmethod
    async def get_ticket_by_id_or_shared(
            session: AsyncSession,
            ticket_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Optional[TicketModels.Get]:
        """
        Retrieves a ticket by ID if it belongs to the user or is marked as shared.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            ticket_id (uuid.UUID): The unique identifier of the ticket.
            user_id (uuid.UUID): The ID of the user requesting the ticket.

        Returns:
            Optional[TicketModels.Get]: A validated Pydantic model of the ticket
                                        if found and accessible, or None otherwise.
        """
        result = await session.execute(
            select(Ticket).where(
                and_(
                    or_(Ticket.user_id == user_id, Ticket.shared is True),
                    Ticket.id == ticket_id
                )
            )
        )

        result = result.scalar_one_or_none()

        return TicketModels.Get.model_validate(result) if result else None

    @staticmethod
    async def get_event_name_for_ticket(
            session: AsyncSession,
            ticket_id: uuid.UUID
    ) -> Optional[str]:
        ticket = await TicketCrud.get_by_id(session=session, record_id=ticket_id)

        if not ticket or (not ticket.event_id and not ticket.custom_event_id):
            return None

        if ticket.event_id:
            event = await EventCrud.get_by_id(session=session, record_id=ticket.event_id)
            return event.name
        elif ticket.custom_event_id:
            event = await CustomEventCrud.get_by_id(session=session, record_id=ticket.event_id)
            return event.name

        return None

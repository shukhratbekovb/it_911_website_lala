from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from cache import redis_cache

from exceptions import NotFound

from filters.contact_filter import ContactFilter
from filters.paginator import Paginator
from filters.sorter import Sorter

from models import Contact

from repository.contact_repo import ContactRepository

from schemas.base import Sort
from schemas.contact import ContactRequest, ContactListResponse


class ContactManager:
    def __init__(self, db: AsyncSession):
        self.repo = ContactRepository(db)

    async def create(
            self,
            request: ContactRequest
    ):
        contact = await self.repo.create(**request.model_dump())
        return contact

    async def update(
            self,
            contact_id,
            request: ContactRequest
    ):
        contact = await self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFound(f"Contact {contact_id} not found")
        contact.full_name = request.full_name
        contact.email = request.email
        contact.phone = request.phone
        contact.lead_id = request.lead_id
        await self.repo.update(contact)

    async def delete(
            self,
            contact_id

    ):
        contact = await self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFound(f"Contact {contact_id} not found")
        await self.repo.delete(contact)

    async def get_by_id(
            self,
            contact_id
    ):
        contact = await self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFound(f"Contact {contact_id} not found")
        return contact

    @redis_cache(prefix="contacts:list", ttl=120)
    async def list(
            self,
            query: str = None,
            created_from: datetime = None,
            created_to: datetime = None,
            sorts: list[Sort] = None,
            page: int = 1,
            size: int = 50
    ):
        filters = ContactFilter(
            query,
            created_from,
            created_to
        )

        sorters = []

        for sort_by in sorts:
            col, destination = sort_by.split(":")
            col = getattr(Contact, col)
            sorters.append((col, destination))

        sorter = Sorter(
            tuple(sorters)
        )

        paginator = Paginator(
            page=page,
            size=size
        )

        contacts = await self.repo.list(
            filters=filters,
            sorter=sorter,
            paginator=paginator,
        )
        return ContactListResponse(
            **contacts
        )

"""Listing aggregate: independent of Django and persistence."""
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from uuid import UUID


class ListingError(ValueError):
    pass


class ListingStatus(str, Enum):
    DRAFT = "draft"
    MODERATION = "moderation"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Listing:
    id: UUID
    owner_id: UUID
    title: str
    daily_rate: Decimal
    deposit: Decimal
    status: ListingStatus = ListingStatus.DRAFT

    def __post_init__(self) -> None:
        if self.daily_rate < 0 or self.deposit < 0:
            raise ListingError("Listing amounts cannot be negative")

    def submit(self) -> "Listing":
        if self.status != ListingStatus.DRAFT or not self.title.strip() or self.daily_rate <= 0:
            raise ListingError("Incomplete draft cannot be submitted")
        return replace(self, status=ListingStatus.MODERATION)

    def approve(self) -> "Listing":
        if self.status != ListingStatus.MODERATION:
            raise ListingError("Only moderated listings can be approved")
        return replace(self, status=ListingStatus.ACTIVE)

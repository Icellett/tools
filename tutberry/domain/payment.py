"""Payment state is separate from the booking aggregate."""
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from uuid import UUID


class PaymentError(ValueError):
    pass


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    FROZEN = "frozen"


@dataclass(frozen=True)
class Payment:
    id: UUID
    booking_id: UUID
    amount: Decimal
    status: PaymentStatus = PaymentStatus.PENDING
    gateway_reference: str | None = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise PaymentError("Payment amount must be positive")

    def confirm(self, gateway_reference: str) -> "Payment":
        if self.status != PaymentStatus.PENDING or not gateway_reference.strip():
            raise PaymentError("Payment confirmation requires a pending operation and provider reference")
        return replace(self, status=PaymentStatus.SUCCESS, gateway_reference=gateway_reference)

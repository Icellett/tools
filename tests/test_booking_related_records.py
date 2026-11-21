"""PostgreSQL checks for the new booking-related tables."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction

from tutberry.models import (
    BookingRecord,
    ListingRecord,
    MessageRecord,
    ReviewRecord,
    TransactionRecord,
)


@pytest.fixture
def booking(db):
    listing = ListingRecord.objects.create(
        owner_id=uuid4(), title="Drill", daily_rate=100, deposit=200, status="active",
    )
    return BookingRecord.objects.create(
        listing=listing, tenant_id=uuid4(), start_date=date(2030, 8, 1),
        end_date=date(2030, 8, 2), rent=Decimal(200), deposit=Decimal(200),
    )


def test_related_records_round_trip(booking):
    payment = TransactionRecord.objects.create(
        booking=booking, amount=Decimal(200), type="rent_payment",
    )
    message = MessageRecord.objects.create(
        booking=booking, sender_id=uuid4(), receiver_id=uuid4(), text_content="Hello",
    )
    review = ReviewRecord.objects.create(
        booking=booking, author_id=uuid4(), target_id=uuid4(), rating=5,
    )
    assert booking.transactions.get().pk == payment.pk
    assert booking.messages.get().pk == message.pk
    assert booking.reviews.get().pk == review.pk


@pytest.mark.django_db(transaction=True)
def test_database_rejects_invalid_payment_and_review(booking):
    with pytest.raises(IntegrityError), transaction.atomic():
        TransactionRecord.objects.create(
            booking=booking, amount=Decimal(-1), type="rent_payment",
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        ReviewRecord.objects.create(
            booking=booking, author_id=uuid4(), target_id=uuid4(), rating=6,
        )
    author = uuid4()
    ReviewRecord.objects.create(booking=booking, author_id=author, target_id=uuid4(), rating=4)
    with pytest.raises(IntegrityError), transaction.atomic():
        ReviewRecord.objects.create(booking=booking, author_id=author, target_id=uuid4(), rating=5)

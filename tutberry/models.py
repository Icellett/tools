"""Persistence models. Domain rules live in tutberry.domain."""
import uuid
from django.db import models


class ListingRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField()
    title = models.CharField(max_length=200)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default="draft")

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(daily_rate__gte=0), name="listing_rate_nonnegative"),
            models.CheckConstraint(condition=models.Q(deposit__gte=0), name="listing_deposit_nonnegative"),
        ]


class BookingRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(ListingRecord, on_delete=models.PROTECT, related_name="bookings")
    tenant_id = models.UUIDField()
    start_date = models.DateField()
    end_date = models.DateField()
    rent = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    cancellation_reason = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(end_date__gte=models.F("start_date")), name="booking_valid_period"),
            models.CheckConstraint(condition=models.Q(rent__gte=0), name="booking_rent_nonnegative"),
            models.CheckConstraint(condition=models.Q(deposit__gte=0), name="booking_deposit_nonnegative"),
        ]

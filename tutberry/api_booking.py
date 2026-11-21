"""Authenticated booking endpoint using server-side listing prices."""
import uuid

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tutberry.adapters.django_booking import DjangoBookingRepository
from tutberry.domain.booking import BookingError
from tutberry.models import ListingRecord
from tutberry.services.booking_service import BookingRequest, BookingService


class CreateBookingSerializer(serializers.Serializer):
    listing_id = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class UuidGenerator:
    def new_id(self):
        return uuid.uuid4()


class NoopNotifier:
    """Notification integration is intentionally deferred to a later lab."""
    def booking_created(self, booking):
        pass


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_booking(request):
    data = CreateBookingSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    values = data.validated_data
    with transaction.atomic():
        try:
            listing = ListingRecord.objects.select_for_update().get(
                id=values["listing_id"], status="active"
            )
        except ListingRecord.DoesNotExist:
            return Response({"detail": "Active listing not found"}, status=status.HTTP_404_NOT_FOUND)

        # Django's integer user ID is converted into a stable domain UUID.
        tenant_id = uuid.uuid5(uuid.NAMESPACE_URL, f"tutberry:user:{request.user.pk}")
        if listing.owner_id == tenant_id:
            return Response({"detail": "Cannot book your own listing"}, status=status.HTTP_400_BAD_REQUEST)
        service = BookingService(DjangoBookingRepository(), UuidGenerator(), NoopNotifier())
        try:
            booking = service.create(
                BookingRequest(
                    listing_id=listing.id,
                    tenant_id=tenant_id,
                    start_date=values["start_date"],
                    end_date=values["end_date"],
                    daily_rate=listing.daily_rate,
                    deposit=listing.deposit,
                )
            )
        except BookingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"id": str(booking.id), "status": booking.status.value, "rent": str(booking.price.rent), "deposit": str(booking.price.deposit), "total": str(booking.price.total)},
        status=status.HTTP_201_CREATED,
    )

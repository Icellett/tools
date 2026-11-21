# Generated for the initial TutBerry persistence schema.
import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="ListingRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("owner_id", models.UUIDField()),
                ("title", models.CharField(max_length=200)),
                ("daily_rate", models.DecimalField(decimal_places=2, max_digits=12)),
                ("deposit", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(default="draft", max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="BookingRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tenant_id", models.UUIDField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("rent", models.DecimalField(decimal_places=2, max_digits=12)),
                ("deposit", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(default="pending", max_length=20)),
                ("cancellation_reason", models.TextField(blank=True, null=True)),
                ("listing", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="tutberry.listingrecord")),
            ],
        ),
        migrations.AddConstraint(model_name="listingrecord", constraint=models.CheckConstraint(condition=models.Q(daily_rate__gte=0), name="listing_rate_nonnegative")),
        migrations.AddConstraint(model_name="listingrecord", constraint=models.CheckConstraint(condition=models.Q(deposit__gte=0), name="listing_deposit_nonnegative")),
        migrations.AddConstraint(model_name="bookingrecord", constraint=models.CheckConstraint(condition=models.Q(end_date__gte=models.F("start_date")), name="booking_valid_period")),
        migrations.AddConstraint(model_name="bookingrecord", constraint=models.CheckConstraint(condition=models.Q(rent__gte=0), name="booking_rent_nonnegative")),
        migrations.AddConstraint(model_name="bookingrecord", constraint=models.CheckConstraint(condition=models.Q(deposit__gte=0), name="booking_deposit_nonnegative")),
    ]

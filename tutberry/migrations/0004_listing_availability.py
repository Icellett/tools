"""Introduce owner-defined listing availability blocks (expand migration)."""
import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tutberry", "0003_booking_query_indexes")]

    operations = [
        migrations.CreateModel(
            name="ListingAvailabilityRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_blocked", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("listing", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="availability_blocks",
                    to="tutberry.listingrecord",
                )),
            ],
        ),
        migrations.AddConstraint(
            model_name="listingavailabilityrecord",
            constraint=models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="availability_valid_period",
            ),
        ),
        migrations.AddIndex(
            model_name="listingavailabilityrecord",
            index=models.Index(fields=["listing", "start_date"], name="availability_listing_start_idx"),
        ),
    ]

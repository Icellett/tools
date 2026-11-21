"""Expand booking schema with transactions, messages and reviews."""
import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tutberry", "0004_listing_availability")]

    operations = [
        migrations.CreateModel(
            name="TransactionRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("amount", models.DecimalField(max_digits=12, decimal_places=2)),
                ("type", models.CharField(max_length=30)),
                ("status", models.CharField(max_length=20, default="pending")),
                ("payment_gateway_id", models.CharField(max_length=200, null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="tutberry.bookingrecord")),
            ],
        ),
        migrations.CreateModel(
            name="MessageRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sender_id", models.UUIDField()),
                ("receiver_id", models.UUIDField()),
                ("text_content", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="messages", to="tutberry.bookingrecord")),
            ],
        ),
        migrations.CreateModel(
            name="ReviewRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("author_id", models.UUIDField()),
                ("target_id", models.UUIDField()),
                ("rating", models.PositiveSmallIntegerField()),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reviews", to="tutberry.bookingrecord")),
            ],
        ),
        migrations.AddConstraint(
            model_name="transactionrecord",
            constraint=models.CheckConstraint(condition=models.Q(amount__gte=0), name="transaction_amount_nonnegative"),
        ),
        migrations.AddConstraint(
            model_name="reviewrecord",
            constraint=models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name="review_rating_1_to_5"),
        ),
        migrations.AddConstraint(
            model_name="reviewrecord",
            constraint=models.UniqueConstraint(fields=["booking", "author_id"], name="review_unique_booking_author"),
        ),
    ]

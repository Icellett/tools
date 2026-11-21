"""Add optional user profiles without rewriting existing booking identifiers."""
import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tutberry", "0005_booking_related_records"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfileRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("display_name", models.CharField(max_length=200)),
                ("phone", models.CharField(max_length=32, blank=True)),
                ("role", models.CharField(max_length=20, default="tenant")),
                ("is_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="tutberry_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="userprofilerecord",
            constraint=models.CheckConstraint(
                condition=models.Q(role__in=["tenant", "owner", "platform"]),
                name="profile_valid_role",
            ),
        ),
    ]

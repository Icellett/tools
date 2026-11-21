"""Integration tests for the optional profile extension."""
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from tutberry.models import UserProfileRecord


@pytest.mark.django_db
def test_profile_belongs_to_django_user():
    user = get_user_model().objects.create_user(username="profile-tenant", password="test-password")
    profile = UserProfileRecord.objects.create(user=user, display_name="Tenant", role="tenant")
    assert user.tutberry_profile.pk == profile.pk
    assert profile.is_verified is False


@pytest.mark.django_db(transaction=True)
def test_profile_role_and_unique_user_constraints():
    user = get_user_model().objects.create_user(username="profile-owner", password="test-password")
    UserProfileRecord.objects.create(user=user, display_name="Owner", role="owner")
    with pytest.raises(IntegrityError), transaction.atomic():
        UserProfileRecord.objects.create(user=user, display_name="Duplicate", role="tenant")
    other = get_user_model().objects.create_user(username="profile-invalid", password="test-password")
    with pytest.raises(IntegrityError), transaction.atomic():
        UserProfileRecord.objects.create(user=other, display_name="Invalid", role="superadmin")

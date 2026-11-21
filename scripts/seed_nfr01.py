"""Create exactly 50,000 active listings for the NFR-01 CI load scenario.

Run on a disposable CI PostgreSQL database, not production.
"""
import os
import uuid
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tutberry.settings")
django.setup()

from tutberry.models import ListingRecord  # noqa: E402


def main() -> None:
    if ListingRecord.objects.exists():
        raise SystemExit("Refusing to seed a nonempty listing table")
    count = 50000
    for start in range(0, count, 2500):
        batch = [
            ListingRecord(
                id=uuid.uuid5(uuid.NAMESPACE_URL, f"tutberry:nfr01:{number}"),
                owner_id=uuid.uuid5(uuid.NAMESPACE_URL, f"tutberry:owner:{number % 1000}"),
                title=f"Repair tool {number}",
                category=("drill" if number % 2 == 0 else "saw"),
                location=("Omsk" if number % 3 == 0 else "Moscow"),
                daily_rate=Decimal(100 + number % 1000),
                deposit=Decimal(500),
                status="active",
            )
            for number in range(start, min(start + 2500, count))
        ]
        ListingRecord.objects.bulk_create(batch, batch_size=2500)
    actual = ListingRecord.objects.filter(status="active").count()
    print(f"Seeded {actual} active listings")
    if actual != count:
        raise SystemExit("Incorrect NFR-01 fixture count")


if __name__ == "__main__":
    main()

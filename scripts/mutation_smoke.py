"""Five reversible fault injections: a test must fail for each mutation.

Run only in a disposable checkout (CI runner). Never run against a working tree
with uncommitted edits: original file contents are restored after every case.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    (
        "M-01 shared date must overlap",
        "tutberry/domain/booking.py",
        "return self.start_date <= other.end_date and other.start_date <= self.end_date",
        "return self.start_date < other.end_date and other.start_date < self.end_date",
        "tests/test_booking_domain.py::test_inclusive_period_and_overlap",
    ),
    (
        "M-02 inclusive day count",
        "tutberry/domain/booking.py",
        "return (self.end_date - self.start_date).days + 1",
        "return (self.end_date - self.start_date).days",
        "tests/test_booking_domain.py::test_inclusive_period_and_overlap",
    ),
    (
        "M-03 deposit contributes to total",
        "tutberry/domain/booking.py",
        "return self.rent + self.deposit",
        "return self.rent",
        "tests/test_booking_service.py::test_booking_created_with_fixed_price_and_notification",
    ),
    (
        "M-04 cancelled booking cannot be approved",
        "tutberry/domain/booking.py",
        "if self.status != BookingStatus.PENDING:",
        "if self.status not in {BookingStatus.PENDING, BookingStatus.CANCELLED}:",
        "tests/test_booking_domain.py::test_booking_lifecycle_and_cancelled_guard",
    ),
    (
        "M-05 owner cannot book own listing",
        "tutberry/api_booking.py",
        "if listing.owner_id == tenant_id:",
        "if False and listing.owner_id == tenant_id:",
        "tests/test_booking_api.py::test_validation_and_owner_permission_problem_details",
    ),
]


def main() -> int:
    caught = 0
    for name, relative_path, original, mutated, test in CASES:
        path = ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        if source.count(original) != 1:
            print(f"ERROR {name}: mutation target not unique or missing", flush=True)
            return 2
        try:
            path.write_text(source.replace(original, mutated, 1), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test, "-q", "-p", "no:cacheprovider"],
                cwd=ROOT,
                check=False,
                timeout=55,
            )
            if result.returncode == 1:
                caught += 1
                print(f"CAUGHT {name}", flush=True)
            else:
                print(f"NOT CAUGHT {name}: pytest exit={result.returncode}", flush=True)
        except subprocess.TimeoutExpired:
            print(f"ERROR {name}: test timed out", flush=True)
        finally:
            path.write_text(source, encoding="utf-8")
    print(f"Mutation detection: {caught}/{len(CASES)}", flush=True)
    return 0 if caught == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())

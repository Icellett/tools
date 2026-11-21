"""Protect tool rental periods at the database level (LR 4A).

RentalPeriod in LR 3 uses inclusive calendar dates. PostgreSQL daterange
is half-open, so the upper bound is end_date + 1 day.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("tutberry", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE EXTENSION IF NOT EXISTS btree_gist;
                ALTER TABLE tutberry_bookingrecord
                ADD CONSTRAINT booking_no_active_overlap
                EXCLUDE USING gist (
                    listing_id WITH =,
                    daterange(start_date, end_date + 1, '[)') WITH &&
                )
                WHERE (status IN ('pending', 'approved', 'paid', 'active'));
            """,
            reverse_sql="""
                ALTER TABLE tutberry_bookingrecord
                DROP CONSTRAINT IF EXISTS booking_no_active_overlap;
            """,
        ),
    ]

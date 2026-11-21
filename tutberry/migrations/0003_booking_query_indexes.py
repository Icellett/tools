"""Indexes supporting the main TutBerry booking queries (LR 4A).

The exclusion constraint already creates a GiST index for overlapping ranges.
These B-tree indexes target different query patterns.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("tutberry", "0002_booking_no_overlap")]

    operations = [
        migrations.RunSQL(
            sql="""
                -- My bookings, newest rental period first.
                CREATE INDEX booking_tenant_recent_idx
                ON tutberry_bookingrecord (tenant_id, start_date DESC);

                -- Active bookings in a requested calendar window.
                CREATE INDEX booking_active_start_idx
                ON tutberry_bookingrecord (start_date)
                WHERE status <> 'cancelled';
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS booking_active_start_idx;
                DROP INDEX IF EXISTS booking_tenant_recent_idx;
            """,
        ),
    ]

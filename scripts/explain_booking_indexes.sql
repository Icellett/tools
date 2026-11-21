-- LR 4A: compare query plans on the same dataset.
-- Run only on a disposable development/test database.
-- These statements run in one transaction and roll back all generated rows.
BEGIN;

-- Use an existing listing; generate non-overlapping single-day bookings.
-- Existing dates are avoided by choosing an isolated future window.
-- The exclusion constraint still applies to every generated row.
WITH selected_listing AS (
    SELECT id FROM tutberry_listingrecord ORDER BY id LIMIT 1
)
INSERT INTO tutberry_bookingrecord
    (id, listing_id, tenant_id, start_date, end_date, rent, deposit, status, cancellation_reason)
SELECT
    gen_random_uuid(), selected_listing.id, gen_random_uuid(),
    DATE '2100-01-01' + i,
    DATE '2100-01-01' + i,
    100.00, 0.00, 'cancelled', NULL
FROM selected_listing, generate_series(0, 29999) AS i;

ANALYZE tutberry_bookingrecord;

-- Compare tenant query without/with the specific B-tree index.
-- Index is dropped temporarily inside a rollback-only transaction.
DROP INDEX IF EXISTS booking_tenant_recent_idx;
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, start_date
FROM tutberry_bookingrecord
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
ORDER BY start_date DESC LIMIT 20;

CREATE INDEX booking_tenant_recent_idx
ON tutberry_bookingrecord (tenant_id, start_date DESC);
ANALYZE tutberry_bookingrecord;
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, start_date
FROM tutberry_bookingrecord
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
ORDER BY start_date DESC LIMIT 20;

ROLLBACK;

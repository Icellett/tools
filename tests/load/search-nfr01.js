// NFR-01: p95 search latency under 300 ms at 20 requests per second.
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    search: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1s',
      duration: '60s',
      preAllocatedVUs: 20,
      maxVUs: 60,
    },
  },
  thresholds: {
    'http_req_duration{endpoint:search}': ['p(95)<300'],
    'http_req_failed': ['rate<0.01'],
    'dropped_iterations': ['count==0'],
    'checks': ['rate>0.99'],
  },
};

const baseUrl = (__ENV.BASE_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');

export default function () {
  // Mixed search selectivity; dates are in a period without fixture bookings.
  const q = __ITER % 3;
  const params = [
    'start_date=2030-06-10&end_date=2030-06-12&category=drill&location=Omsk',
    'start_date=2030-06-10&end_date=2030-06-12&max_price=350',
    'start_date=2030-06-10&end_date=2030-06-12',
  ][q];
  const response = http.get(`${baseUrl}/api/listings?${params}`, {
    tags: { endpoint: 'search' },
  });
  check(response, {
    'search returns HTTP 200': (r) => r.status === 200,
    'search has items': (r) => {
      if (r.status !== 200) return false;
      try {
        const body = r.json();
        return Array.isArray(body.items) && body.items.length > 0;
      } catch (_) {
        return false;
      }
    },
  });
}

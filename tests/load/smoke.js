// TutBerry k6 smoke: проверка доступного GET /health.
// НЕ является доказательством NFR-01: endpoint поиска пока не реализован.
// Запуск: k6 run -e BASE_URL=http://localhost:8080 tests/load/smoke.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 10,
      maxVUs: 50,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<300'],
  },
};

const baseUrl = (__ENV.BASE_URL || 'http://localhost:8080').replace(/\/$/, '');

export default function () {
  const response = http.get(`${baseUrl}/health`, { tags: { endpoint: 'health' } });
  check(response, { 'health returns 200': (r) => r.status === 200 });
}

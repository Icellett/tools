// TutBerry k6 saturation: рост нагрузки на GET /health, вне CI.
// НЕ проверяет NFR-01 по поиску и не заменяет базу из 50 000 объявлений.
// Запуск: k6 run -e BASE_URL=http://localhost:8080 tests/load/saturation.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    saturation: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 20,
      maxVUs: 150,
      stages: [
        { target: 10, duration: '1m' },
        { target: 20, duration: '1m' },
        { target: 40, duration: '1m' },
        { target: 80, duration: '1m' },
        { target: 0, duration: '30s' },
      ],
    },
  },
};

const baseUrl = (__ENV.BASE_URL || 'http://localhost:8080').replace(/\/$/, '');

export default function () {
  const response = http.get(`${baseUrl}/health`, { tags: { endpoint: 'health' } });
  check(response, { 'health returns 200': (r) => r.status === 200 });
}

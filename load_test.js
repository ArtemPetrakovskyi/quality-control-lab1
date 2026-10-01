import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '30s', target: 20 },
    { duration: '5s', target: 0 },
  ],

  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.02'],
  },
};

export default function () {
  const userId = Math.floor(Math.random() * 1000) + 1;

  const res = http.get(`http://localhost:8000/api/v1/users/${userId}`);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(0.1);
}
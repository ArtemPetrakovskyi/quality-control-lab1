import pytest
from fastapi.testclient import TestClient
from main import app
from logger_config import privacy_logger, PrivacyFilter
import logging
import io

client = TestClient(app)

def test_secure_logging_masking():
    log_output = io.StringIO()
    handler = logging.StreamHandler(log_output)
    handler.addFilter(PrivacyFilter())

    test_logger = logging.getLogger("test_privacy")
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)

    # Відправляємо відкритий email і пароль
    test_logger.info("User ivan.test@example.com logged in with password=secret123")

    result_text = log_output.getvalue()

    # Перевіряємо, що сирих даних НЕМАЄ в логу
    assert "ivan.test@example.com" not in result_text
    assert "secret123" not in result_text
    # Перевіряємо, що маскування виконано
    assert "i***@example.com" in result_text
    assert "password=[REDACTED]" in result_text

def test_personal_data_export():
    # Позитивний сценарій
    response = client.get("/api/users/1/personal-data?request_actor_id=1")
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "password_hash" not in data["profile"]  # Мінімізація (пароль виключено!)

    # Негативний сценарій (чужий ID)
    fail_response = client.get("/api/users/1/personal-data?request_actor_id=2")
    assert fail_response.status_code == 403


def test_anonymization_workflow():
    response = client.post("/api/users/1/anonymize?request_actor_id=1")
    assert response.status_code == 200

    # Перевіряємо через експорт, що дані стали анонімними
    export_res = client.get("/api/users/1/personal-data?request_actor_id=1")
    profile = export_res.json()["profile"]
    assert profile["name"] == "Anonymous User"
    assert profile["email"] == "deleted_1@anon.local"


def test_consent_policy_gate():
    # 1. Даємо згоду (GRANT)
    client.post("/api/consents/grant?user_id=1&purpose=MARKETING")

    # 2. Перевіряємо ALLOW (дії дозволено)
    allow_res = client.post("/api/marketing/send?user_id=1")
    assert allow_res.status_code == 200

    # 3. Відкликаємо згоду (REVOKE)
    client.post("/api/consents/revoke?user_id=1&purpose=MARKETING")

    # 4. Перевіряємо DENY (дію заблоковано)
    deny_res = client.post("/api/marketing/send?user_id=1")
    assert deny_res.status_code == 403
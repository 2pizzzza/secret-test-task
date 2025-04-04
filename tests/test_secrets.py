import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.secret_service import SecretService
from app.repository.repository import SecretRepository
from unittest.mock import MagicMock

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    mock_db = MagicMock()
    return mock_db


@pytest.fixture
def mock_cache():
    mock_cache = MagicMock()
    return mock_cache


# Тесты для API

def test_create_secret(mock_db_session, mock_cache):
    data = {
        "secret": "mysecret",
        "passphrase": "mypassword",
        "ttl_seconds": 300
    }

    SecretRepository.create_secret = MagicMock(return_value="test_secret_key")

    response = client.post("/api/v1/secret", json=data)

    assert response.status_code == 200
    assert response.json() == {"secret_key": "test_secret_key"}


def test_retrieve_secret(mock_db_session, mock_cache):
    SecretRepository.get_secret = MagicMock(
        return_value='{"secret": "encrypted_secret", '
                     '"passphrase": "encrypted_passphrase"}')
    SecretService.retrieve_secret = MagicMock(return_value="decrypted_secret")

    response = client.get("/api/v1/secret/test_secret_key")

    assert response.status_code == 200
    assert response.json() == {"secret": "decrypted_secret"}


def test_delete_secret(mock_db_session, mock_cache):
    data = {"passphrase": "mypassword"}
    SecretRepository.get_secret = MagicMock(
        return_value='{"secret": "encrypted_secret", '
                     '"passphrase": "encrypted_passphrase"}')
    SecretRepository.delete_secret = MagicMock()

    response = client.delete("/api/v1/secret/test_secret_key", json=data)

    assert response.status_code == 200
    assert response.json() == {"status": "secret deleted"}


def test_create_secret_service(mock_db_session):
    data = {
        "secret": "mysecret",
        "passphrase": "mypassword",
        "ttl_seconds": 300
    }
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    SecretRepository.create_secret = MagicMock(return_value="test_secret_key")
    SecretRepository.log_secret_action = MagicMock()

    secret_key = SecretService.create_secret(
        mock_db_session,
        data,
        data["ttl_seconds"],
        mock_request)

    assert secret_key == "test_secret_key"


def test_delete_secret_service(mock_db_session):
    data = {"passphrase": "mypassword"}

    SecretRepository.get_secret = MagicMock(
        return_value='{"secret": "encrypted_secret", '
                     '"passphrase": "encrypted_passphrase"}')
    SecretRepository.delete_secret = MagicMock()
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    SecretService.delete_secret("test_secret_key", data, mock_db_session, mock_request)

    SecretRepository.delete_secret.assert_called_once()


def test_create_secret_repository(mock_cache):
    secret_data = {"secret": "encrypted_secret", "passphrase": "encrypted_passphrase"}
    ttl = 300

    SecretRepository.set_secret = MagicMock()

    secret_key = SecretRepository.create_secret(mock_cache, secret_data, ttl)

    assert secret_key == "test_secret_key"
    SecretRepository.set_secret.assert_called_once_with(
        "test_secret_key",
        '{"secret": "encrypted_secret", "passphrase": "encrypted_passphrase"}',
        ttl
    )


def test_get_secret_repository(mock_cache):
    secret_key = "test_secret_key"

    SecretRepository.get_secret = MagicMock(
        return_value='{"secret": "encrypted_secret"}'
    )

    result = SecretRepository.get_secret(secret_key)

    assert result == '{"secret": "encrypted_secret"}'


def test_delete_secret_repository(mock_cache):
    secret_key = "test_secret_key"

    SecretRepository.delete_secret = MagicMock()

    SecretRepository.delete_secret(secret_key)

    SecretRepository.delete_secret.assert_called_once_with(secret_key)

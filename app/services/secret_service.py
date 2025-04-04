from fastapi import HTTPException
from app.repository.repository import SecretRepository
from app.services.encryption import encrypt_secret, decrypt_secret
import json


class SecretService:

    @staticmethod
    def create_secret(db, data, ttl, request):
        secret_data = {
            "secret": encrypt_secret(data.secret),
            "passphrase": encrypt_secret(data.passphrase) if data.passphrase else None
        }
        secret_key = SecretRepository.create_secret(db, secret_data, ttl)
        SecretRepository.log_secret_action(db, "created", secret_key, request)
        return secret_key

    @staticmethod
    def delete_secret(secret_key, data, db, request):
        encrypted_data = SecretRepository.get_secret(secret_key)
        if not encrypted_data:
            raise HTTPException(status_code=404, detail="Secret not found or expired")

        secret_data = json.loads(encrypted_data)
        stored_passphrase = secret_data["passphrase"]

        if (stored_passphrase and
                (not data.passphrase or decrypt_secret(stored_passphrase)
                 != data.passphrase)):
            raise HTTPException(status_code=403, detail="Invalid passphrase")

        SecretRepository.delete_secret(secret_key)
        SecretRepository.log_secret_action(db, "deleted", secret_key, request)

    @staticmethod
    def retrieve_secret(secret_key, db, request):
        encrypted_data = SecretRepository.get_secret(secret_key)
        if not encrypted_data:
            raise HTTPException(status_code=404, detail="Secret not found or expired")

        secret_data = json.loads(encrypted_data)
        secret = decrypt_secret(secret_data["secret"])
        SecretRepository.delete_secret(secret_key)
        SecretRepository.log_secret_action(db, "retrieved", secret_key, request)
        return secret

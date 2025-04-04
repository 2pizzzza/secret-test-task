from sqlalchemy.orm import Session
from app.services.cache import set_secret, get_secret, delete_secret
from app.models.secret_log import SecretLog
import json
import uuid


class SecretRepository:

    @staticmethod
    def create_secret(db: Session, secret_data: dict, ttl: int):
        secret_key = str(uuid.uuid4())
        set_secret(secret_key, json.dumps(secret_data), ttl)
        return secret_key

    @staticmethod
    def delete_secret(secret_key: str):
        delete_secret(secret_key)

    @staticmethod
    def get_secret(secret_key: str):
        return get_secret(secret_key)

    @staticmethod
    def log_secret_action(db: Session, action: str, secret_key: str, request):
        log = SecretLog(
            secret_key=secret_key,
            action=action,
            ip_address=request.client.host,
            extra_data=""
        )
        db.add(log)
        db.commit()

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.database import get_db
from app.services.cache import set_secret, get_secret, delete_secret
from app.services.encryption import encrypt_secret, decrypt_secret
from app.models.secret_log import SecretLog
import uuid

router = APIRouter()


class SecretCreate(BaseModel):
    secret: str
    passphrase: str | None = None
    ttl_seconds: int | None = 300


class SecretResponse(BaseModel):
    secret_key: str


class SecretRetrieve(BaseModel):
    secret: str


@router.post("/secret", response_model=SecretResponse)
async def create_secret(
        data: SecretCreate,
        request: Request,
        db: Session = Depends(get_db)
):
    secret_key = str(uuid.uuid4())

    encrypted_secret = encrypt_secret(data.secret)

    ttl = data.ttl_seconds if data.ttl_seconds else 300
    set_secret(secret_key, encrypted_secret, ttl)

    log = SecretLog(
        secret_key=secret_key,
        action="created",
        ip_address=request.client.host,
        extra_data=f"ttl={ttl}"
    )
    db.add(log)
    db.commit()

    return {"secret_key": secret_key}


@router.get("/secret/{secret_key}", response_model=SecretRetrieve)
async def retrieve_secret(
        secret_key: str,
        request: Request,
        db: Session = Depends(get_db)
):
    encrypted_secret = get_secret(secret_key)
    if not encrypted_secret:
        raise HTTPException(status_code=404, detail="Secret not found or expired")

    secret = decrypt_secret(encrypted_secret)

    delete_secret(secret_key)

    log = SecretLog(
        secret_key=secret_key,
        action="retrieved",
        ip_address=request.client.host
    )
    db.add(log)
    db.commit()

    return {
        "secret": secret,
        "headers": {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    }


@router.delete("/secret/{secret_key}")
async def delete_secret_endpoint(
        secret_key: str,
        request: Request,
        db: Session = Depends(get_db)
):
    if not get_secret(secret_key):
        raise HTTPException(status_code=404, detail="Secret not found or expired")

    delete_secret(secret_key)

    log = SecretLog(
        secret_key=secret_key,
        action="deleted",
        ip_address=request.client.host
    )
    db.add(log)
    db.commit()

    return {"status": "secret deleted"}
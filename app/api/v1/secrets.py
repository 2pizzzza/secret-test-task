from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.secret_service import SecretService
from app.services.database import get_db


router = APIRouter()


class SecretCreate(BaseModel):
    secret: str
    passphrase: str | None = None
    ttl_seconds: int | None = 300


class SecretResponse(BaseModel):
    secret_key: str


class SecretRetrieve(BaseModel):
    secret: str


class SecretDelete(BaseModel):
    passphrase: str | None = None


@router.post("/secret", response_model=SecretResponse)
async def create_secret(
        data: SecretCreate,
        request: Request,
        db: Session = Depends(get_db)):
    secret_key = SecretService.create_secret(db, data, data.ttl_seconds, request)
    return {"secret_key": secret_key}


@router.delete("/secret/{secret_key}")
async def delete_secret_endpoint(
        secret_key: str,
        request: Request,
        data: SecretDelete = Depends(),
        db: Session = Depends(get_db)):
    SecretService.delete_secret(secret_key, data, db, request)
    return {"status": "secret deleted"}


@router.get("/secret/{secret_key}", response_model=SecretRetrieve)
async def retrieve_secret(
        secret_key: str,
        request: Request,
        db: Session = Depends(get_db)):
    secret = SecretService.retrieve_secret(secret_key, db, request)
    return {"secret": secret}

import asyncio
from fastapi import FastAPI
from app.api.v1 import secrets
from app.services.database import Base, engine, get_db
from app.services.cache import redis_client
from app.models.secret_log import SecretLog

app = FastAPI(
    title="Disposable Secrets",
    description="Service for storing one-time secrets",
    version="1.0.0"
)

app.include_router(secrets.router, prefix="/api/v1", tags=["secrets"])

Base.metadata.create_all(bind=engine)


async def cleanup_expired_secrets():
    while True:
        db = next(get_db())
        try:
            keys = redis_client.keys("*")
            for key in keys:
                if redis_client.ttl(key) <= 0:
                    redis_client.delete(key)
                    log = SecretLog(
                        secret_key=key,
                        action="expired",
                        ip_address="system",
                        extra_data="auto_cleanup"
                    )
                    db.add(log)
                    db.commit()
        finally:
            db.close()
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_expired_secrets())


@app.get("/")
async def root():
    return {"message": "Welcome to Disposable Secrets"}

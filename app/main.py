from fastapi import FastAPI
from app.api.v1 import secrets
from app.services.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Disposable Secrets",
    description="Service for storing one-time secrets",
    version="1.0.0"
)

app.include_router(secrets.router, prefix="/api/v1", tags=["secrets"])


@app.get("/")
async def root():
    return {"message": "Welcome to Disposable Secrets"}

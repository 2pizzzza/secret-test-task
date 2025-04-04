from sqlalchemy import Column, Integer, String, DateTime, func
from app.services.database import Base

class SecretLog(Base):
    __tablename__ = "secret_logs"

    id = Column(Integer, primary_key=True, index=True)
    secret_key = Column(String, index=True)  #
    action = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    extra_data = Column(String, nullable=True)
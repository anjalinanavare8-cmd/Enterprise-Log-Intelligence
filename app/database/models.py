
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)

from app.database.connection import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String(50), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))
    level = Column(String(20), nullable=False)
    error_code = Column(String(50))
    message = Column(Text, nullable=False)
    response_time = Column(Float)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(30), unique=True, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))
    severity = Column(String(20), nullable=False)
    status = Column(String(30), default="Open")
    detection_method = Column(String(50))
    reasons = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AuditHistory(Base):
    __tablename__ = "audit_history"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    action = Column(String(200), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


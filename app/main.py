
from fastapi import FastAPI

from app.database.connection import Base, engine
from app.database import models

from app.api.routes.logs import router as logs_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.services import router as services_router

app = FastAPI(
    title="Enterprise Log Intelligence Platform",
    description="API for log monitoring, anomaly detection and incident management.",
    version="1.0.0",
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Enterprise Log Intelligence Platform API is running!",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }


app.include_router(logs_router)
app.include_router(incidents_router)
app.include_router(services_router)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Log, Service
from app.api.schemas.log import LogCreate

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/")
def create_log(
    log_data: LogCreate,
    db: Session = Depends(get_db),
):
    try:
        level = log_data.level.upper()

        if level not in {"INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid log level",
            )

        service = db.query(Service).filter(
            Service.name == log_data.service
        ).first()

        if not service:
            service = Service(name=log_data.service)
            db.add(service)
            db.flush()

        new_log = Log(
            timestamp=log_data.timestamp,
            service_id=service.id,
            level=level,
            error_code=log_data.error_code,
            message=log_data.message,
            response_time=log_data.response_time,
        )

        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return {
            "message": "Log saved successfully",
            "log_id": new_log.id,
            "service": service.name,
            "level": new_log.level,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Could not save log: {error}",
        )


@router.get("/")
def get_logs(
    service: str | None = None,
    level: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Log, Service.name).join(
        Service, Log.service_id == Service.id
    )

    if service:
        query = query.filter(Service.name == service)

    if level:
        query = query.filter(Log.level == level.upper())

    results = query.order_by(Log.id.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "timestamp": log.timestamp,
            "service": service_name,
            "level": log.level,
            "error_code": log.error_code,
            "message": log.message,
            "response_time": log.response_time,
        }
        for log, service_name in results
    ]


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.database.models import Log, Service

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/")
def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).order_by(Service.name).all()

    result = []

    for service in services:
        logs = db.query(Log).filter(
            Log.service_id == service.id
        ).all()

        total_logs = len(logs)

        errors = sum(
            1 for log in logs
            if log.level in ["ERROR", "CRITICAL"]
        )

        warnings = sum(
            1 for log in logs
            if log.level == "WARNING"
        )

        error_rate = (
            (errors / total_logs) * 100
            if total_logs > 0 else 0
        )

        response_times = [
            log.response_time
            for log in logs
            if log.response_time is not None
        ]

        average_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0
        )

        if error_rate >= 50:
            health = "CRITICAL"
        elif error_rate >= 20:
            health = "WARNING"
        else:
            health = "HEALTHY"

        result.append({
            "service": service.name,
            "total_logs": total_logs,
            "errors": errors,
            "warnings": warnings,
            "error_rate_percent": round(error_rate, 2),
            "average_response_time_ms": round(
                average_response_time, 2
            ),
            "health": health,
        })

    return {
        "total_services": len(result),
        "services": result,
    }


@router.get("/{service_name}")
def get_service_details(
    service_name: str,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(
        func.lower(Service.name) == service_name.lower()
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    logs = db.query(Log).filter(
        Log.service_id == service.id
    ).order_by(Log.id.desc()).all()

    return {
        "service": service.name,
        "total_logs": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "level": log.level,
                "error_code": log.error_code,
                "message": log.message,
                "response_time": log.response_time,
            }
            for log in logs
        ],
    }

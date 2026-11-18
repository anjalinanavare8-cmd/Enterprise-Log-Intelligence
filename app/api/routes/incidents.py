
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from app.database.connection import get_db
from app.database.models import Incident, Service, AuditHistory
from app.api.schemas.incident import (
    IncidentCreate,
    IncidentStatusUpdate,
)
from app.analytics.anomaly_detection import AnomalyDetector


router = APIRouter(prefix="/incidents", tags=["Incidents"])


# 1. GET ALL INCIDENTS
@router.get("/")
def get_incidents(
    status: str | None = None,
    severity: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Incident, Service.name).join(
        Service,
        Incident.service_id == Service.id
    )

    if status:
        query = query.filter(Incident.status == status)

    if severity:
        query = query.filter(Incident.severity == severity.upper())

    results = query.order_by(
        Incident.id.desc()
    ).limit(limit).all()

    return [
        {
            "id": incident.id,
            "incident_code": incident.incident_code,
            "service": service_name,
            "severity": incident.severity,
            "status": incident.status,
            "detection_method": incident.detection_method,
            "reasons": json.loads(incident.reasons or "[]"),
            "created_at": incident.created_at,
        }
        for incident, service_name in results
    ]


# 2. CREATE INCIDENT MANUALLY
@router.post("/")
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(Incident).filter(
        Incident.incident_code == incident_data.incident_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Incident code already exists",
        )

    service = db.query(Service).filter(
        Service.name == incident_data.service
    ).first()

    if not service:
        service = Service(name=incident_data.service)
        db.add(service)
        db.flush()

    new_incident = Incident(
        incident_code=incident_data.incident_code,
        service_id=service.id,
        severity=incident_data.severity.upper(),
        status="Open",
        detection_method=incident_data.detection_method,
        reasons=json.dumps(incident_data.reasons),
    )

    db.add(new_incident)
    db.flush()

    audit = AuditHistory(
        incident_id=new_incident.id,
        action="Incident created",
        notes="Incident registered through API",
    )

    db.add(audit)
    db.commit()
    db.refresh(new_incident)

    return {
        "message": "Incident created successfully",
        "id": new_incident.id,
        "incident_code": new_incident.incident_code,
        "service": service.name,
        "severity": new_incident.severity,
        "status": new_incident.status,
    }


# 3. AUTOMATIC ANOMALY DETECTION AND INCIDENT CREATION
@router.post("/detect-anomalies")
def detect_anomalies_and_create_incidents(
    db: Session = Depends(get_db),
):
    try:
        result = AnomalyDetector().detect_database(db)

        detected = result["anomalies"]

        # Group multiple detections for the same service
        grouped = {}

        for anomaly in detected:
            service_name = anomaly["service"]

            if service_name not in grouped:
                grouped[service_name] = {
                    "service": service_name,
                    "error_rate_percent": anomaly["error_rate_percent"],
                    "methods": set(),
                    "reasons": set(),
                }

            grouped[service_name]["methods"].add(
                anomaly["detection_method"]
            )

            for reason in anomaly["reasons"]:
                grouped[service_name]["reasons"].add(reason)

        created_incidents = []
        skipped_incidents = []

        for service_name, data in grouped.items():

            service = db.query(Service).filter(
                Service.name == service_name
            ).first()

            if not service:
                continue

            # Do not create another active incident
            existing = db.query(Incident).filter(
                Incident.service_id == service.id,
                Incident.status.in_(["Open", "Investigating"])
            ).first()

            if existing:
                skipped_incidents.append({
                    "service": service_name,
                    "existing_incident": existing.incident_code,
                    "reason": "Active incident already exists",
                })
                continue

            error_rate = data["error_rate_percent"]

            if error_rate >= 80:
                severity = "CRITICAL"
            elif error_rate >= 50:
                severity = "HIGH"
            else:
                severity = "MEDIUM"

            methods = sorted(data["methods"])
            reasons = sorted(data["reasons"])

            detection_method = " + ".join(methods)

            # Generate a unique incident code
            last_incident = db.query(Incident).order_by(
                Incident.id.desc()
            ).first()

            next_number = (
                last_incident.id + 1
                if last_incident else 1
            )

            incident_code = f"ANOM-{next_number:04d}"

            new_incident = Incident(
                incident_code=incident_code,
                service_id=service.id,
                severity=severity,
                status="Open",
                detection_method=detection_method,
                reasons=json.dumps(reasons),
            )

            db.add(new_incident)
            db.flush()

            audit = AuditHistory(
                incident_id=new_incident.id,
                action="Incident created by anomaly detection",
                notes=(
                    f"Automatically detected for {service_name}. "
                    f"Methods: {detection_method}. "
                    f"Reasons: {', '.join(reasons)}"
                ),
            )

            db.add(audit)

            created_incidents.append({
                "incident_code": incident_code,
                "service": service_name,
                "severity": severity,
                "status": "Open",
                "detection_method": detection_method,
                "reasons": reasons,
            })

        db.commit()

        return {
            "message": "Anomaly detection completed",
            "total_services_analyzed": result["total_services"],
            "total_anomalies_detected": len(detected),
            "incidents_created": len(created_incidents),
            "existing_incidents_skipped": len(skipped_incidents),
            "created_incidents": created_incidents,
            "skipped_incidents": skipped_incidents,
        }

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(error)}",
        )


# 4. UPDATE INCIDENT STATUS
@router.patch("/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    update: IncidentStatusUpdate,
    db: Session = Depends(get_db),
):
    allowed_statuses = {
        "Open",
        "Investigating",
        "Resolved",
        "Closed",
    }

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident status",
        )

    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    incident.status = update.status
    incident.updated_at = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    audit = AuditHistory(
        incident_id=incident.id,
        action=f"Status changed to {update.status}",
        notes=update.note,
    )

    db.add(audit)
    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident updated successfully",
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
        "status": incident.status,
        "note": update.note,
    }

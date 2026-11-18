
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class IncidentService:
    """Creates and manages incidents from detected anomalies."""

    def __init__(self, storage_file: str = "reports/incidents.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_incidents(self) -> list[dict[str, Any]]:
        if not self.storage_file.exists():
            return []

        with self.storage_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save_incidents(self, incidents: list[dict[str, Any]]) -> None:
        with self.storage_file.open("w", encoding="utf-8") as file:
            json.dump(incidents, file, indent=4)

    @staticmethod
    def _get_severity(anomaly: dict[str, Any]) -> str:
        error_rate = anomaly.get("error_rate_percent", 0)

        if error_rate >= 80:
            return "CRITICAL"
        elif error_rate >= 50:
            return "HIGH"
        return "MEDIUM"

    def create_from_anomalies(
        self, anomalies: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        incidents = self._load_incidents()
        created = []

        for anomaly in anomalies:
            service = anomaly.get("service", "Unknown")
            method = anomaly.get("detection_method", "Unknown")
            reasons = anomaly.get("reasons", [])

            # Avoid creating the same active incident repeatedly.
            already_open = any(
                item["service"] == service
                and item["detection_method"] == method
                and item["reasons"] == reasons
                and item["status"] != "Closed"
                for item in incidents
            )

            if already_open:
                continue

            incident = {
                "incident_id": f"INC-{len(incidents) + 1:04d}",
                "service": service,
                "severity": self._get_severity(anomaly),
                "detection_method": method,
                "reasons": reasons,
                "status": "Open",
                "investigation_notes": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "audit_history": [
                    {
                        "action": "Incident created",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            }

            incidents.append(incident)
            created.append(incident)

        self._save_incidents(incidents)
        return created

    def update_status(
        self, incident_id: str, new_status: str, note: str = ""
    ) -> dict[str, Any]:

        allowed_statuses = {
            "Open", "Investigating", "Resolved", "Closed"
        }

        if new_status not in allowed_statuses:
            raise ValueError("Invalid incident status.")

        incidents = self._load_incidents()

        for incident in incidents:
            if incident["incident_id"] == incident_id:
                incident["status"] = new_status
                incident["updated_at"] = datetime.now(
                    timezone.utc
                ).isoformat()

                if note:
                    incident["investigation_notes"].append(note)

                incident["audit_history"].append({
                    "action": f"Status changed to {new_status}",
                    "timestamp": incident["updated_at"],
                })

                self._save_incidents(incidents)
                return incident

        raise ValueError(f"Incident not found: {incident_id}")

    def get_all_incidents(self) -> list[dict[str, Any]]:
        return self._load_incidents()

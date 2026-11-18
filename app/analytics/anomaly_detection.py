
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """Detect unusual service behaviour using rules and machine learning."""

    def _analyse(self, df: pd.DataFrame) -> dict:

        if df.empty:
            return {
                "total_services": 0,
                "anomalies": [],
                "service_analysis": [],
            }

        required = {"service", "level", "response_time"}
        missing = required - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {', '.join(sorted(missing))}"
            )

        df = df.copy()
        df["level"] = df["level"].astype(str).str.upper()
        df["response_time"] = pd.to_numeric(
            df["response_time"], errors="coerce"
        )

        service_data = []

        for service, group in df.groupby("service"):

            total = len(group)

            errors = int(
                group["level"].isin(["ERROR", "CRITICAL"]).sum()
            )

            warnings = int(
                (group["level"] == "WARNING").sum()
            )

            error_rate = errors / total * 100
            avg_response = group["response_time"].mean()

            service_data.append({
                "service": str(service),
                "total_logs": total,
                "errors": errors,
                "warnings": warnings,
                "error_rate_percent": round(error_rate, 2),
                "average_response_time_ms": round(
                    float(avg_response)
                    if pd.notna(avg_response) else 0.0,
                    2
                ),
            })

        features = pd.DataFrame(service_data)

        # Store detected anomalies
        anomalies = []

        # 1. RULE-BASED DETECTION
        for item in service_data:

            reasons = []

            if item["error_rate_percent"] >= 50:
                reasons.append("High error rate")

            if item["average_response_time_ms"] >= 2000:
                reasons.append("High average response time")

            if reasons:
                anomalies.append({
                    **item,
                    "detection_method": "Rule-based",
                    "reasons": reasons,
                })

        # 2. MACHINE LEARNING DETECTION
        if len(features) >= 3:

            model_features = features[
                [
                    "total_logs",
                    "errors",
                    "error_rate_percent",
                    "average_response_time_ms",
                ]
            ]

            model = IsolationForest(
                n_estimators=100,
                contamination=0.25,
                random_state=42,
            )

            predictions = model.fit_predict(model_features)

            for index, prediction in enumerate(predictions):

                if prediction == -1:

                    item = service_data[index]

                    anomalies.append({
                        **item,
                        "detection_method": "Isolation Forest",
                        "reasons": [
                            "Unusual service behaviour detected by ML"
                        ],
                    })

        return {
            "total_services": len(service_data),
            "anomalies": anomalies,
            "service_analysis": service_data,
        }

    # Analyse an existing CSV file
    def detect(self, file_path: str) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Log file not found: {path}"
            )

        df = pd.read_csv(path)

        return self._analyse(df)

    # Analyse logs directly from SQLite database
    def detect_database(self, db) -> dict:

        from app.database.models import Log, Service

        results = (
            db.query(
                Log.level,
                Log.response_time,
                Service.name.label("service")
            )
            .join(Service, Log.service_id == Service.id)
            .all()
        )

        records = [
            {
                "service": row.service,
                "level": row.level,
                "response_time": row.response_time,
            }
            for row in results
        ]

        df = pd.DataFrame(
            records,
            columns=["service", "level", "response_time"]
        )

        return self._analyse(df)

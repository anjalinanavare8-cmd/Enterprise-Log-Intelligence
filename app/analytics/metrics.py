
import pandas as pd
from pathlib import Path

class ServiceMetrics:
    """Calculates service health and performance metrics."""

    def analyze(self, file_path: str) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Processed log file not found: {path}"
            )

        df = pd.read_csv(path)

        if df.empty:
            return {
                "total_logs": 0,
                "service_summary": [],
            }

        required_columns = {
            "service",
            "level",
            "response_time",
        }

        missing = required_columns - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {', '.join(sorted(missing))}"
            )

        df["level"] = df["level"].astype(str).str.upper()
        df["response_time"] = pd.to_numeric(
            df["response_time"], errors="coerce"
        )

        summary = []

        for service, group in df.groupby("service"):

            total = len(group)
            errors = int(
                group["level"].isin(["ERROR", "CRITICAL"]).sum()
            )
            warnings = int(
                (group["level"] == "WARNING").sum()
            )

            error_rate = round((errors / total) * 100, 2)

            average_response = group["response_time"].mean()

            if error_rate >= 50:
                health = "CRITICAL"
            elif error_rate >= 20:
                health = "WARNING"
            else:
                health = "HEALTHY"

            summary.append({
                "service": service,
                "total_logs": total,
                "errors": errors,
                "warnings": warnings,
                "error_rate_percent": error_rate,
                "average_response_time_ms": (
                    round(float(average_response), 2)
                    if pd.notna(average_response)
                    else None
                ),
                "health_status": health,
            })

        return {
            "total_logs": len(df),
            "service_summary": summary,
        }
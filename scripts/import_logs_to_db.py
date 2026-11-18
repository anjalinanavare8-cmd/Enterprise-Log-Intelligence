
import csv
from pathlib import Path

from app.database.connection import SessionLocal
from app.database.models import Log, Service

# Find the project folder automatically
PROJECT_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = PROJECT_DIR / "data" / "raw" / "sample_logs.csv"


def import_logs():
    db = SessionLocal()

    imported = 0
    skipped = 0

    try:
        if not CSV_FILE.exists():
            print("ERROR: Sample CSV file not found:", CSV_FILE)
            return

        with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                timestamp = row["timestamp"].strip()
                service_name = row["service"].strip()
                level = row["level"].strip().upper()
                error_code = row["error_code"].strip()
                message = row["message"].strip()

                response_time = row.get("response_time")

                if response_time:
                    response_time = float(response_time)
                else:
                    response_time = None

                # Find or create the service
                service = db.query(Service).filter(
                    Service.name == service_name
                ).first()

                if service is None:
                    service = Service(name=service_name)
                    db.add(service)
                    db.flush()

                # Prevent importing the same record twice
                existing_log = db.query(Log).filter(
                    Log.timestamp == timestamp,
                    Log.service_id == service.id,
                    Log.level == level,
                    Log.error_code == error_code,
                    Log.message == message,
                    Log.response_time == response_time
                ).first()

                if existing_log:
                    skipped += 1
                    continue

                new_log = Log(
                    timestamp=timestamp,
                    service_id=service.id,
                    level=level,
                    error_code=error_code,
                    message=message,
                    response_time=response_time
                )

                db.add(new_log)
                imported += 1

        db.commit()

        print("\n========== IMPORT SUMMARY ==========")
        print("CSV file:", CSV_FILE.name)
        print("New logs imported:", imported)
        print("Duplicate logs skipped:", skipped)

        total_logs = db.query(Log).count()
        total_services = db.query(Service).count()

        print("Total database logs:", total_logs)
        print("Total database services:", total_services)
        print("IMPORT COMPLETED SUCCESSFULLY!")

    except Exception as error:
        db.rollback()
        print("IMPORT FAILED:", error)

    finally:
        db.close()


if __name__ == "__main__":
    import_logs()

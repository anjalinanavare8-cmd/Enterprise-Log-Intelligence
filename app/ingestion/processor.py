
import csv
from pathlib import Path
from typing import Any

from app.ingestion.parsers import LogParser
from app.ingestion.validators import LogValidator


class LogProcessor:
    """Processes, validates, deduplicates and saves log records."""

    def __init__(self):
        self.parser = LogParser()
        self.validator = LogValidator()

    def process_file(
        self,
        file_path: str,
        output_dir: str = "data/processed",
    ) -> dict[str, Any]:

        valid_records = []
        rejected_records = []
        seen_records = set()

        total_records = 0
        duplicate_records = 0

        # Read records one by one.
        for record in self.parser.parse_file(file_path):
            total_records += 1

            is_valid, cleaned_record, reason = (
                self.validator.validate(record)
            )

            if not is_valid:
                rejected_records.append({
                    **record,
                    "reason": reason,
                })
                continue

            # Create a unique signature for duplicate detection.
            signature = (
                cleaned_record["timestamp"],
                cleaned_record["service"],
                cleaned_record["level"],
                cleaned_record["error_code"],
                cleaned_record["message"],
            )

            if signature in seen_records:
                duplicate_records += 1
                continue

            seen_records.add(signature)
            valid_records.append(cleaned_record)

        # Create output directory.
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        valid_file = output_path / "processed_logs.csv"
        rejected_file = output_path / "rejected_logs.csv"

        self._save_csv(valid_records, valid_file)
        self._save_csv(rejected_records, rejected_file)

        return {
            "total_records": total_records,
            "valid_records": len(valid_records),
            "rejected_records": len(rejected_records),
            "duplicate_records": duplicate_records,
            "saved_valid_file": str(valid_file),
            "saved_rejected_file": str(rejected_file),
        }

    @staticmethod
    def _save_csv(
        records: list[dict[str, Any]],
        file_path: Path,
    ) -> None:

        if not records:
            file_path.write_text("", encoding="utf-8")
            return

        fieldnames = list(
            dict.fromkeys(
                key
                for record in records
                for key in record.keys()
            )
        )

        with file_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(records)

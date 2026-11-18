
from datetime import datetime, timezone
from typing import Any


class LogValidator:
    """Checks and standardizes individual log records."""

    REQUIRED_FIELDS = [
        "timestamp",
        "service",
        "level",
        "error_code",
        "message",
    ]

    VALID_LEVELS = {"INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"}

    def validate(
        self, record: dict[str, Any]
    ) -> tuple[bool, dict[str, Any], str | None]:

        # Reject records that could not be parsed.
        if "_parse_error" in record:
            return False, {}, str(record["_parse_error"])

        cleaned = {
            str(key).strip(): (
                value.strip() if isinstance(value, str) else value
            )
            for key, value in record.items()
        }

        # Check required fields.
        for field in self.REQUIRED_FIELDS:
            value = cleaned.get(field)

            if value is None or str(value).strip() == "":
                return False, {}, f"Missing required field: {field}"

        # Validate and standardize timestamp.
        try:
            timestamp_text = str(cleaned["timestamp"])
            parsed_time = datetime.fromisoformat(
                timestamp_text.replace("Z", "+00:00")
            )

            # Treat timestamps without a timezone as UTC.
            if parsed_time.tzinfo is None:
                parsed_time = parsed_time.replace(tzinfo=timezone.utc)

            cleaned["timestamp"] = (
                parsed_time.astimezone(timezone.utc).isoformat()
            )

        except (ValueError, TypeError):
            return False, {}, "Invalid timestamp format"

        # Validate log level.
        cleaned["level"] = str(cleaned["level"]).upper()

        if cleaned["level"] not in self.VALID_LEVELS:
            return False, {}, "Invalid log level"

        # Validate response time when supplied.
        response_time = cleaned.get("response_time")

        if response_time not in (None, ""):
            try:
                response_time = float(response_time)

                if response_time < 0:
                    return False, {}, "Response time cannot be negative"

                cleaned["response_time"] = response_time

            except (ValueError, TypeError):
                return False, {}, "Response time must be numeric"
        else:
            cleaned["response_time"] = None

        # Standardize text fields.
        for field in ("service", "error_code", "message"):
            cleaned[field] = str(cleaned[field]).strip()

        return True, cleaned, None

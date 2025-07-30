import json
import logging


def _parse_log_json(json_output: str) -> list[dict]:
    """Parses the JSON string from PowerShell into a list of log dictionaries."""
    if not json_output.strip():
        return []
    try:
        logs = json.loads(json_output)
        # The script might return a single object if there's only one log
        if isinstance(logs, dict):
            return [logs]
        return logs
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from PowerShell output: {json_output}")
        return []

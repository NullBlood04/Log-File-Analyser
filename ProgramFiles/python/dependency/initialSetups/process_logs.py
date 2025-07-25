import chromadb
from datetime import datetime, timezone
from dotenv import load_dotenv
import subprocess
import json
import os
import logging

# Local imports
from ..AdditionalTools.sqlConnection import ConnectDBase

# Configure logging for better diagnostics
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Configuration ---
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")

# Make chroma-db directory if it doesn't exist
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
POWERSHELL_SCRIPT_PATH = os.path.join(
    PROJECT_ROOT, "ProgramFiles", "powershell", "extract_logs.ps1"
)

type storeProcess = tuple[list, list, list, list, int]


def get_bookmark(bookmark: str) -> int:
    """
    Safely reads the last recorded event record ID from the bookmark file.
    If the file doesn't exist, it creates one and returns 0.
    """
    if not os.path.exists(bookmark):
        try:
            with open(bookmark, "w") as f:
                f.write("0")
            return 0
        except IOError as e:
            logging.error(f"Could not create bookmark file at {bookmark}: {e}")
            raise
    try:
        with open(bookmark, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (IOError, ValueError) as e:
        logging.error(f"Could not read or parse bookmark file at {bookmark}: {e}")
        raise


def update_bookmark(bookmark_path: str, record_id: int) -> None:
    """Writes the given record ID to the bookmark file."""
    try:
        with open(bookmark_path, "w") as f:
            f.write(str(record_id))
        logging.info(f"Bookmark updated to record ID: {record_id}")
    except IOError as e:
        logging.error(f"Failed to write to bookmark file at {bookmark_path}: {e}")
        # Decide if this should re-raise or just log


def sanitise_datetime(timestamp: str) -> datetime:
    # Converts a .NET JSON date format to a timezone-aware datetime object.
    try:
        in_milliseconds = int(timestamp.strip("/Date()"))
        return datetime.fromtimestamp(in_milliseconds / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        logging.warning(f"Could not parse timestamp: {timestamp}. Using current time.")
        return datetime.now(timezone.utc)


def _run_powershell_script(log_name: str, last_record_id: int) -> str | None:
    """Executes the PowerShell script to extract logs and returns the JSON output."""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                POWERSHELL_SCRIPT_PATH,
                str(last_record_id),
                log_name,
            ],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout
    except FileNotFoundError:
        logging.error(f"PowerShell script not found at {POWERSHELL_SCRIPT_PATH}")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"PowerShell script failed with error: {e.stderr}")
        return None


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


def _process_and_store_logs(
    logs: list[dict], log_name: str, last_record_id: int
) -> storeProcess:
    """Processes logs and prepares them for database insertion."""
    sql_batch = []
    chroma_docs, chroma_metadatas, chroma_ids = [], [], []
    max_record_id = last_record_id

    for log in logs:
        try:
            record_id = int(log["RecordId"])
            event_id = int(log["Id"])
            provider_name = log["ProviderName"]
            time_created = sanitise_datetime(log["TimeCreated"])
            message = log["Message"]

            # Prepare batch for SQL
            sql_batch.append(
                (
                    record_id,
                    event_id,
                    log["LevelDisplayName"],
                    provider_name,
                    time_created,
                )
            )

            # Prepare batch for ChromaDB
            sentence = f"Error registered at: {log_name} log, occurred for {provider_name} at {time_created.isoformat()} with EventID: {event_id} having Message: {message}"
            chroma_docs.append(sentence)
            chroma_metadatas.append(
                {
                    "event_log": log_name,
                    "source": provider_name,
                    "event_id": event_id,
                    "timestamp_utc": time_created.isoformat(),
                    "record_id": record_id,
                }
            )
            chroma_ids.append(f"{log_name}_{event_id}_{record_id}")

            if record_id > max_record_id:
                max_record_id = record_id
        except (KeyError, TypeError, ValueError) as e:
            logging.warning(f"Skipping malformed log entry: {log}. Error: {e}")
            continue

    return sql_batch, chroma_docs, chroma_metadatas, chroma_ids, max_record_id


def process_new_logs(
    log_name: str,
    bookmark_path: str,
    sql_con: ConnectDBase,
    collection: chromadb.Collection,
) -> None:
    """
    Orchestrates the extraction, processing, and storage of new Windows Event Logs.
    """
    last_record_id = get_bookmark(bookmark_path)
    logging.info(
        f"Starting log processing for '{log_name}' from record ID: {last_record_id}"
    )

    json_output = _run_powershell_script(log_name, last_record_id)
    if not json_output:
        return  # Error already logged in helper

    logs = _parse_log_json(json_output)
    if not logs:
        logging.info(f"No new logs to process for '{log_name}'.")
        return

    sql_batch, chroma_docs, chroma_metadatas, chroma_ids, max_record_id = (
        _process_and_store_logs(logs, log_name, last_record_id)
    )

    if not sql_batch:
        logging.info(f"No valid logs were processed for '{log_name}'.")
        return

    # Use a transaction to ensure both databases are updated or neither is.
    try:
        sql_query = f"INSERT INTO {log_name}_logs (RecordId, EventID, Level, Source, TimeCreated) VALUES (%s, %s, %s, %s, %s)"
        if sql_con.execute_many(sql_query, sql_batch):
            collection.add(
                documents=chroma_docs, metadatas=chroma_metadatas, ids=chroma_ids
            )
            sql_con.connection.commit()  # type: ignore
            logging.info(
                f"Successfully committed {len(sql_batch)} new '{log_name}' log entries."
            )
            update_bookmark(bookmark_path, max_record_id)
        else:
            raise Exception("SQL batch execution failed.")

    except Exception as e:
        logging.error(
            f"Transaction failed for '{log_name}'. Rolling back changes. Error: {e}"
        )
        try:
            if sql_con.is_connected():
                sql_con.connection.rollback()  # type: ignore
        except Exception as rb_e:
            logging.error(f"Failed to rollback transaction: {rb_e}")

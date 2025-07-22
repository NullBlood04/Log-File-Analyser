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

# Use a single, unified bookmark file.
BOOKMARK_PATH = os.getenv(
    "RECORD_PATH", os.path.join(PROJECT_ROOT, "TextFiles", "last_recordedId.txt")
)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")
POWERSHELL_SCRIPT_PATH = os.path.join(
    PROJECT_ROOT, "ProgramFiles", "powershell", "extract_logs.ps1"
)


def get_bookmark() -> int:
    """
    Safely reads the last recorded event record ID from the bookmark file.
    If the file doesn't exist, it creates one and returns 0.
    """
    if not os.path.exists(BOOKMARK_PATH):
        try:
            with open(BOOKMARK_PATH, "w") as f:
                f.write("0")
            return 0
        except IOError as e:
            logging.error(f"Could not create bookmark file at {BOOKMARK_PATH}: {e}")
            raise
    try:
        with open(BOOKMARK_PATH, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (IOError, ValueError) as e:
        logging.error(f"Could not read or parse bookmark file at {BOOKMARK_PATH}: {e}")
        raise


def sanitise_datetime(timestamp: str) -> datetime:
    # Converts a .NET JSON date format to a timezone-aware datetime object.
    try:
        in_milliseconds = int(timestamp.strip("/Date()"))
        return datetime.fromtimestamp(in_milliseconds / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        logging.warning(f"Could not parse timestamp: {timestamp}. Using current time.")
        return datetime.now(timezone.utc)


def process_new_logs() -> None:
    """
    Extracts new Windows Event Logs and updates both the SQL and ChromaDB databases.
    """
    last_record_id = get_bookmark()
    logging.info(f"Starting log processing from record ID: {last_record_id}")

    # Step 1: Extract logs using PowerShell
    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                POWERSHELL_SCRIPT_PATH,
                f"{last_record_id}",
            ],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        logging.error(f"PowerShell script not found at {POWERSHELL_SCRIPT_PATH}")
        return
    except subprocess.CalledProcessError as e:
        logging.error(f"PowerShell script failed with error: {e.stderr}")
        return

    if not result.stdout.strip():
        logging.info("No new logs to process.")
        return

    # Step 2: Parse logs
    try:
        logs = json.loads(result.stdout)
        if isinstance(logs, dict):
            logs = [logs]
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from PowerShell output: {result.stdout}")
        return

    if not logs:
        logging.info("No new logs found after parsing.")
        return

    # Step 3: Connect to Databases
    user, password = os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD")
    sql_con = ConnectDBase(user, password, "log")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection(name="windows_event_logs")

    if not sql_con.is_connected():
        logging.error("Aborting: Could not establish SQL database connection.")
        return

    # Step 4: Process and insert logs
    chroma_docs, chroma_metadatas, chroma_ids = [], [], []
    max_record_id = last_record_id
    sql_inserted_count = 0

    for log in logs:
        # --- Prepare data for both databases ---
        record_id = int(log["RecordId"])
        event_id = int(log["Id"])
        provider_name = log["ProviderName"]
        time_created = sanitise_datetime(log["TimeCreated"])
        message = log["Message"]

        # --- SQL Insertion ---
        sql_query = (
            "INSERT INTO application_errors "
            "(RecordId, EventID, Level, Source, TimeCreated) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        sql_data = (
            record_id,
            event_id,
            log["LevelDisplayName"],
            provider_name,
            time_created,
        )
        if sql_con.execute_query(sql_query, sql_data):
            sql_inserted_count += 1

        # --- ChromaDB Preparation ---
        sentence = f"Error occurred for {provider_name} at {time_created.isoformat()} with EventID: {event_id} having Message: {message}"
        chroma_docs.append(sentence)
        chroma_metadatas.append(
            {
                "source": provider_name,
                "event_id": event_id,
                "timestamp_utc": time_created.isoformat(),
                "record_id": record_id,
            }
        )
        chroma_ids.append(f"{provider_name}_{record_id}")

        if record_id > max_record_id:
            max_record_id = record_id

    # Step 5: Finalize operations
    if chroma_docs:
        try:
            collection.add(
                documents=chroma_docs, metadatas=chroma_metadatas, ids=chroma_ids
            )
            logging.info(f"Successfully added {len(chroma_docs)} entries to ChromaDB.")
        except Exception as e:
            logging.error(f"Failed to add embeddings to ChromaDB: {e}")

    if sql_inserted_count > 0:
        logging.info(f"Successfully inserted {sql_inserted_count} entries into SQL DB.")

    if max_record_id > last_record_id:
        with open(BOOKMARK_PATH, "w") as f:
            f.write(str(max_record_id))
        logging.info(f"Bookmark updated to record ID: {max_record_id}")

    sql_con.disconnect_sql()


if __name__ == "__main__":
    process_new_logs()

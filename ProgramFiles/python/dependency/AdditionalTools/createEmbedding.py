import chromadb
from datetime import datetime, timezone
from dotenv import load_dotenv
import subprocess
import json
import os
import logging

load_dotenv()

# Configure logging for better diagnostics
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# It's good practice to define constants for paths and check for their existence.
# Constructing absolute paths makes your script more robust and independent of the current working directory.
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
RECORD_PATH = os.getenv(
    "RECORD_PATH", os.path.join(PROJECT_ROOT, "last_recordedId.txt")
)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")
POWERSHELL_SCRIPT_PATH = os.path.join(
    PROJECT_ROOT, "ProgramFiles", "powershell", "extract_logs.ps1"
)

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_bookmark() -> int:
    """
    Safely reads the last recorded event record ID from the bookmark file.
    If the file doesn't exist, it creates one and returns 0.
    """
    if not os.path.exists(RECORD_PATH):
        try:
            with open(RECORD_PATH, "w") as record_file:
                record_file.write("0")
            return 0
        except IOError as e:
            logging.error(f"Could not create bookmark file at {RECORD_PATH}: {e}")
            raise
    else:
        try:
            with open(RECORD_PATH, "r") as record_file:
                last_record_id_str = record_file.read().strip()
                return int(last_record_id_str) if last_record_id_str else 0
        except (IOError, ValueError) as e:
            logging.error(
                f"Could not read or parse bookmark file at {RECORD_PATH}: {e}"
            )
            raise


def sanitise_datetime(timestamp: str) -> datetime:
    """Converts a .NET JSON date format to a timezone-aware datetime object."""
    try:
        # Assumes format like "/Date(1624482702000)/"
        in_milliseconds = int(timestamp.strip("/Date()"))
        in_seconds = in_milliseconds / 1000
        return datetime.fromtimestamp(in_seconds, tz=timezone.utc)
    except (ValueError, TypeError):
        logging.warning(f"Could not parse timestamp: {timestamp}. Using current time.")
        return datetime.now(timezone.utc)


# Create an embedding index for the logs.
def create_embedding() -> None:
    """
    Extracts new Windows Event Logs, creates sentence embeddings,
    and stores them in a ChromaDB collection.
    """
    # Get the last record ID
    last_record_id = get_bookmark()
    logging.info(f"Starting log extraction from record ID: {last_record_id}")

    # Extract Application.evtx into json format
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
            check=True,  # Raise an exception for non-zero exit codes
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

    try:
        logs = json.loads(result.stdout)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from PowerShell output: {result.stdout}")
        return

    if not logs:
        logging.info("No new logs found.")
        return

    if isinstance(logs, dict):
        logs = [logs]

    documents, metadatas, ids = [], [], []
    max_record_id = last_record_id

    for log in logs:
        if not all(
            k in log
            for k in ["ProviderName", "Id", "Message", "RecordId", "TimeCreated"]
        ):
            logging.warning(f"Skipping malformed log entry: {log}")
            continue

        temp_time = sanitise_datetime(log["TimeCreated"])
        # Use the correct keys from the PowerShell script output
        sentence = f"Error occurred for {log['ProviderName']} at {temp_time.isoformat()} with EventID: {log['Id']} having Message: {log['Message']}"
        documents.append(sentence)

        metadatas.append(
            {
                "source": log["ProviderName"],
                "event_id": log["Id"],
                "timestamp_utc": temp_time.isoformat(),
                "record_id": int(log["RecordId"]),
            }
        )
        ids.append(
            f"{log['ProviderName']}_{log['RecordId']}"
        )  # Create a more unique ID

        record_id = int(log["RecordId"])
        if record_id > max_record_id:
            max_record_id = record_id

    if not documents:
        logging.info("No valid logs to add to the database.")
        return

    try:
        collection = chroma_client.get_or_create_collection(name="windows_event_logs")
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logging.info(
            f"Successfully added {len(documents)} new log entries to ChromaDB."
        )

        # Update bookmark only after successful DB insertion
        with open(RECORD_PATH, "w") as record_file:
            record_file.write(str(max_record_id))
        logging.info(f"Bookmark updated to record ID: {max_record_id}")

    except Exception as e:
        logging.error(f"Failed to add embeddings to ChromaDB: {e}")


if __name__ == "__main__":
    create_embedding()

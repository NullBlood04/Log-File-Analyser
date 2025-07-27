import chromadb
from dotenv import load_dotenv
import os
import logging

# Local imports
from . import PROJECT_ROOT
from ..AdditionalTools.sqlConnection import ConnectDBase
from .setupTools.runScript import _run_powershell_script
from .setupTools.jsonParse import _parse_log_json
from .setupTools.getBookmark import get_bookmark
from .setupTools.processStore import _process_and_store_logs


# Configure logging for better diagnostics
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Configuration ---

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")

# Make chroma-db directory if it doesn't exist
os.makedirs(CHROMA_DB_PATH, exist_ok=True)


def prepare_log_batch(log_name: str, bookmark_path: str):
    """
    Fetches and processes new logs, returning them ready for storage.
    """
    last_record_id = get_bookmark(bookmark_path)
    json_output = _run_powershell_script(log_name, last_record_id)
    if not json_output:
        return None

    logs = _parse_log_json(json_output)
    if not logs:
        return None

    # This function just returns the processed data
    sql_batch, chroma_docs, chroma_metadatas, chroma_ids, max_record_id = (
        _process_and_store_logs(logs, log_name, last_record_id)
    )

    # Return everything needed for the final commit
    return {
        "sql_batch": sql_batch,
        "sql_query": f"INSERT INTO {log_name}_logs (RecordId, EventID, Level, Source, TimeCreated) VALUES (%s, %s, %s, %s, %s)",
        "chroma_docs": chroma_docs,
        "chroma_metadatas": chroma_metadatas,
        "chroma_ids": chroma_ids,
        "bookmark_path": bookmark_path,
        "max_record_id": max_record_id,
    }


def prepare_log_batch_debug(json_path: str) -> dict | None:
    import re

    """
    purpose: For debugging purposes, this function reads a JSON file
    containing logs and processes them without running the PowerShell script.
    """
    with open(json_path, "r", encoding="utf-8-sig") as f:
        json_output = f.read()
    logs = _parse_log_json(json_output)
    if not logs:
        return None

    # This function just returns the processed data
    sql_batch, chroma_docs, chroma_metadatas, chroma_ids, max_record_id = (
        _process_and_store_logs(logs, json_path, 0)
    )

    # Return everything needed for the final commit
    return {
        "sql_batch": sql_batch,
        "sql_query": "INSERT INTO log_name_logs (RecordId, EventID, Level, Source, TimeCreated) VALUES (%s, %s, %s, %s, %s)",
        "chroma_docs": chroma_docs,
        "chroma_metadatas": chroma_metadatas,
        "chroma_ids": chroma_ids,
        "bookmark_path": None,
        "max_record_id": max_record_id,
    }

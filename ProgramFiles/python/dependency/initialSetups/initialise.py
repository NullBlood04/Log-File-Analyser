import os
import logging
import chromadb
from dotenv import load_dotenv

# Local imports from the 'dependency' package
from dependency.initialSetups.process_logs import process_new_logs
from dependency.initialSetups.createDatabase import create_errorDbase
from dependency.AdditionalTools.sqlConnection import ConnectDBase

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Configuration ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

# Use separate bookmark files for each log type to track progress independently.
BOOKMARK_PATH_APP = os.getenv(
    "APP_BOOKMARK", os.path.join(PROJECT_ROOT, "TextFiles", "last_app_id.txt")
)
BOOKMARK_PATH_SYS = os.getenv(
    "SYS_BOOKMARK", os.path.join(PROJECT_ROOT, "TextFiles", "last_sys_id.txt")
)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")


def run_processing():
    """
    Initializes database connections and runs the log processing for
    both Application and System event logs. This function serves as the
    main entry point for the log ingestion pipeline.
    """
    logging.info("--- Starting Log Processing Cycle ---")

    # 1. Ensure database schema exists before processing.
    create_errorDbase()

    # 2. Establish shared database connections.
    sql_con = None
    try:
        user, password = os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD")
        # Connect to the 'log' database, consistent with createDatabase.py
        sql_con = ConnectDBase(user, password, "log")

        # The ChromaDB client is file-based and should be instantiated once.
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = chroma_client.get_or_create_collection(name="windows_event_logs")

        if sql_con.is_connected():
            # 3. Process logs for each specified log type using the shared connections.
            process_new_logs("Application", BOOKMARK_PATH_APP, sql_con, collection)
            process_new_logs("System", BOOKMARK_PATH_SYS, sql_con, collection)
        else:
            logging.error("Could not connect to SQL database. Log processing skipped.")

    except Exception as e:
        logging.error(f"A critical error occurred during the log processing cycle: {e}")
    finally:
        # 4. Ensure the SQL connection is always closed to release resources.
        if sql_con and sql_con.is_connected():
            sql_con.disconnect_sql()
        logging.info("--- Log Processing Cycle Finished ---")


if __name__ == "__main__":
    run_processing()

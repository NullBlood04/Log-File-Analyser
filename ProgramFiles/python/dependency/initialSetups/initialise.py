import os
import logging
import chromadb
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Local imports from the 'dependency' package
from .process_logs import (
    prepare_log_batch,
)
from .setupTools import update_bookmark
from .createDatabase import create_errorDbase
from ..AdditionalTools import ConnectDBase
from .. import PROJECT_ROOT

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Configuration ---
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

# Use separate bookmark files for each log type to track progress independently.
BOOKMARK_PATH_APP = os.getenv(
    "APP_BOOKMARK", os.path.join(PROJECT_ROOT, "TextFiles", "last_app_id.txt")
)
BOOKMARK_PATH_SYS = os.getenv(
    "SYS_BOOKMARK", os.path.join(PROJECT_ROOT, "TextFiles", "last_sys_id.txt")
)
CHROMA_DB_PATH = "C:\\chromadb"


def run_processing():
    """
    Initializes database connections and runs the log processing for
    both Application and System event logs. This function serves as the
    main entry point for the log ingestion pipeline.
    """
    logging.info("--- Starting Log Processing Cycle ---")

    create_errorDbase()
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    sql_con = None

    try:
        user, password = os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD")

        sql_con = ConnectDBase(user, password, "log")

        # Define the embedding function consistently. This is crucial for preventing index corruption.
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = chroma_client.get_or_create_collection(
            name="windows_event_logs", embedding_function=embedding_fn  # type: ignore
        )

        if sql_con.is_connected():

            sys_data = prepare_log_batch("System", BOOKMARK_PATH_SYS)
            app_data = prepare_log_batch("Application", BOOKMARK_PATH_APP)

            """ app_data = prepare_log_batch_debug(r"JSON\\application_logs.json")
            sys_data = prepare_log_batch_debug(r"JSON\\system_logs.json") """

            logging.info("Processing Application and System logs...")

            all_docs = []
            all_metadatas = []
            all_ids = []

            if app_data:
                all_docs.extend(app_data["chroma_docs"])
                all_metadatas.extend(app_data["chroma_metadatas"])
                all_ids.extend(app_data["chroma_ids"])

            if sys_data:
                all_docs.extend(sys_data["chroma_docs"])
                all_metadatas.extend(sys_data["chroma_metadatas"])
                all_ids.extend(sys_data["chroma_ids"])

            # Perform all database operations together
            try:
                if all_ids:
                    # First, execute SQL queries
                    if app_data:

                        sql_con.execute_many(
                            app_data["sql_query"], app_data["sql_batch"]
                        )

                        logging.info(
                            f"Successfully added {len(app_data['sql_batch'])} new Application log entries."
                        )

                    if sys_data:

                        sql_con.execute_many(
                            sys_data["sql_query"], sys_data["sql_batch"]
                        )

                        logging.info(
                            f"Successfully added {len(sys_data['sql_batch'])} new System log entries."
                        )

                    # Then, add to Chroma in ONE call
                    collection.add(
                        documents=all_docs, metadatas=all_metadatas, ids=all_ids
                    )

                    logging.info(
                        f"Successfully added {len(all_ids)} documents to ChromaDB."
                    )

                    # Finally, commit and update bookmarks
                    sql_con.connection.commit()  # type: ignore

                    if app_data:

                        update_bookmark(
                            app_data["bookmark_path"], app_data["max_record_id"]
                        )

                    if sys_data:

                        update_bookmark(
                            sys_data["bookmark_path"], sys_data["max_record_id"]
                        )

                    logging.info("Transaction successful.")

            except Exception as e:
                logging.error(f"Transaction failed: {e}")
                sql_con.connection.rollback()  # type: ignore

    # ... finally close connection ...

    except Exception as e:
        logging.error(f"A critical error occurred: {e}")
        if sql_con and sql_con.is_connected():
            sql_con.connection.rollback()  # type: ignore
    finally:
        if sql_con and sql_con.is_connected():
            sql_con.disconnect_sql()
        logging.info("--- Log Processing Cycle Finished ---")


if __name__ == "__main__":
    run_processing()

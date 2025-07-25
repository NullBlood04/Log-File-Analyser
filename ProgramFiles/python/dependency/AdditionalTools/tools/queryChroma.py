import chromadb
from langchain.tools import tool
import os
from dotenv import load_dotenv
import logging

# --- Configuration (as before) ---
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# --- Create a single, shared client instance ---
try:
    CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    # Get the collection once to be reused by the tool
    WINDOWS_LOGS_COLLECTION = CHROMA_CLIENT.get_or_create_collection(
        name="windows_event_logs"
    )
    logging.info("Successfully connected to ChromaDB and loaded collection.")
except Exception as e:
    logging.critical(f"Failed to initialize ChromaDB client: {e}")
    # Set to None so the tool can handle the failure gracefully
    WINDOWS_LOGS_COLLECTION = None


# --- Your Tool ---
@tool(parse_docstring=True)
def query_chroma(query: str, where_filter: dict | None = None):
    """
    Queries ChromaDB for logs similar to a query, optionally filtered by metadata.

    Filters:
    - "source" (str): Log provider name
    - "event_id" (int): Event ID
    - "record_id" (int): Record ID
    - "event_log" (str): Log type (e.g., "Application", "System")
    - "timestamp" (str): Timestamp in ISO format

    Args:
        query (str): Search query.
        where_filter (dict, optional): Metadata filter.

    Returns:
        str: Relevant log entries or a message if none found.
    """
    logging.info(f"Querying ChromaDB with query: {query} and filter: {where_filter}")

    # Check if the collection was initialized successfully
    if WINDOWS_LOGS_COLLECTION is None:
        return "Error: ChromaDB collection is not available. Check application logs."

    try:
        # Use the pre-initialized collection object
        results = WINDOWS_LOGS_COLLECTION.query(
            query_texts=[query], n_results=5, where=where_filter
        )

        print(results)

        documents = results.get("documents")
        if not documents or not documents[0]:
            return "No relevant log entries found for the given query and/or filter."

        full_output = "\n---\n".join(documents[0])

        max_output_length = 4000
        if len(full_output) > max_output_length:
            truncated_output = full_output[:max_output_length]
            return f"{truncated_output}\n... (truncated, showing a subset of the most relevant results)"

        return full_output
    except ValueError as e:
        logging.error(f"ChromaDB query failed with invalid filter: {e}")
        return f"Error during ChromaDB query, possibly an invalid filter: {e}"
    except Exception as e:
        logging.error(f"An error occurred during ChromaDB query: {e}")
        return f"An unexpected error occurred while querying the log database: {e}"

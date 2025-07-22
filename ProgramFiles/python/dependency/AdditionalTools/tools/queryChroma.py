from langchain.tools import tool
import chromadb
from dotenv import load_dotenv
import os
import logging


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromaDB")
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@tool(parse_docstring=True)
def query_chroma(query: str, where_filter: dict | None = None):
    """
    Queries ChromaDB for logs similar to a query, optionally filtered by metadata.

    Filters:
    - "source" (str): Log provider name
    - "event_id" (int): Event ID
    - "record_id" (int): Record ID

    Args:
        query (str): Search query.
        where_filter (dict, optional): Metadata filter.

    Returns:
        str: Relevant log entries or a message if none found.
    """
    logging.info(f"Querying ChromaDB with query: {query} and filter: {where_filter}")

    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        # Use get_or_create_collection for robustness. This prevents errors
        # if the collection doesn't exist yet (e.g., on a fresh run with no new logs).
        collection = chroma_client.get_or_create_collection(name="windows_event_logs")

        results = collection.query(query_texts=[query], n_results=2, where=where_filter)

        documents = results.get("documents")
        if not documents or not documents[0]:
            return "No relevant log entries found for the given query and/or filter."

        # Join the documents into a single plain text string, separated by newlines.
        # This is cleaner for an LLM to process.
        return "\n".join(documents[0])

    except ValueError as e:
        # This can happen if the where_filter is invalid.
        logging.error(f"ChromaDB query failed with invalid filter: {e}")
        return f"Error during ChromaDB query, possibly an invalid filter: {e}"
    except Exception as e:
        logging.error(f"An error occurred during ChromaDB query: {e}")
        return f"An unexpected error occurred while querying the log database: {e}"

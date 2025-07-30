type storeProcess = tuple[list, list, list, list, int]

from .datetime import sanitise_datetime
import logging


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

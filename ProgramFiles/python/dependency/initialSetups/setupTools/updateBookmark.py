import logging


def update_bookmark(bookmark_path: str, record_id: int) -> None:
    """Writes the given record ID to the bookmark file."""
    try:
        with open(bookmark_path, "w") as f:
            f.write(str(record_id))
        logging.info(f"Bookmark updated to record ID: {record_id}")
    except IOError as e:
        logging.error(f"Failed to write to bookmark file at {bookmark_path}: {e}")

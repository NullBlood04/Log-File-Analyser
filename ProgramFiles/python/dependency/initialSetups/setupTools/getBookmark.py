import os
import logging


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

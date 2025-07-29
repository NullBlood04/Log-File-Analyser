import time
import logging
from dependency import run_processing

# Configure logging to see output from the processing task
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """
    Main function to run the log processing task.
    This can be scheduled to run periodically.
    """
    logging.info("--- Starting Scheduled Log Processing Run ---")
    run_processing()
    logging.info("--- Log Processing Run Finished ---")


if __name__ == "__main__":
    # This script is intended to be run on a schedule (e.g., every 15 minutes).
    # For a single execution, you can just run: python run_log_processor.py
    main()

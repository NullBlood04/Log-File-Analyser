import logging
import datetime
import os
from .initialise import run_processing
from .. import PROJECT_ROOT

# Configure logging to see output from the processing task
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

LAST_RUN_DATE = os.getenv(
    "LAST_RUN", os.path.join(PROJECT_ROOT, "TextFiles", "last_run_date.txt")
)


def daily_run():
    """
    Main function to run the log processing task, but only once per day.
    This checks if the processing has already run today before proceeding.
    """
    today = datetime.date.today()

    try:
        if os.path.exists(LAST_RUN_DATE):
            try:
                with open(LAST_RUN_DATE, "r") as f:
                    last_run_date_str = f.read().strip()
                    last_run_date = (
                        datetime.datetime.strptime(
                            last_run_date_str, r"%Y-%m-%d"
                        ).date()
                        if last_run_date_str
                        else None
                    )
            except (ValueError, FileNotFoundError):
                logging.warning(
                    "Could not read last run date, assuming it hasn't run today."
                )
                last_run_date = None
        else:
            last_run_date = None

        if last_run_date != today:
            logging.info("--- Starting Daily Log Processing Run ---")
            run_processing()
            logging.info("--- Log Processing Run Finished ---")

            try:
                with open(LAST_RUN_DATE, "w") as f:
                    f.write(today.strftime("%Y-%m-%d"))
            except IOError as e:
                logging.error(f"Failed to write last run date to file: {e}")

        else:
            logging.info("Log processing already run today.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

from datetime import datetime, timezone
from dotenv import load_dotenv
import subprocess
import json
import os

# Local imports
from .sqlConnection import ConnectDBase

load_dotenv()

RECORD_PATH = os.getenv("RECORD_PATH")


def data_insert() -> None:

    # Safely read the last recorded serial number for
    if not os.path.exists(f"{RECORD_PATH}"):
        with open(f"{RECORD_PATH}", "w") as record_file:
            record_file.write("0")
        last_record_id = 0

    else:
        with open(f"{RECORD_PATH}", "r") as record_file:
            last_record_id = record_file.read()

    # Extract Application.evtx into json format

    result = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "ProgramFiles\\powershell\\extract_logs.ps1",
            f"{last_record_id}",
        ],
        capture_output=True,
        text=True,
    )

    # If `result` has values
    try:
        # Establish Database Connection
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        con = ConnectDBase(user, password, "log")

        logs = json.loads(result.stdout)

        # This handles the case where only one log entry is returned
        if isinstance(logs, dict):
            logs = [logs]

        # Convert JSON .NET date format to ISO format
        def sanitise_datetime(timestamp: str):
            in_milliseconds = int(timestamp.strip("/Date()").strip("/"))
            in_seconds = in_milliseconds / 1000
            return datetime.fromtimestamp(in_seconds, tz=timezone.utc)

        max_record_id = int(last_record_id)

        # Adding the field into Database
        for entry in logs:
            query = (
                "INSERT INTO application_errors "
                "(EventID, Level, Source, TimeCreated, Message) "
                "VALUES( %s, %s, %s, %s, %s)"
            )

            data = (
                entry["Id"],
                entry["LevelDisplayName"],
                entry["ProviderName"],
                sanitise_datetime(entry["TimeCreated"]),
                entry["Message"],
            )

            con.execute_query(query, data)
            record_id = entry["RecordId"]
            if record_id and max_record_id < record_id:
                max_record_id = record_id

        with open(f"{RECORD_PATH}", "w") as record_file:
            record_file.write(str(max_record_id))

        con.disconnect_sql()

    # If `result` does not have values
    except json.decoder.JSONDecodeError:
        print("no field to append")

    finally:
        print("Successfully executed the program")


if __name__ == "__main__":
    data_insert()

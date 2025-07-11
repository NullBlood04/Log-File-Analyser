from datetime import datetime, timezone
from dotenv import load_dotenv
import subprocess
import json
import os

# Local imports
from .sqlConnection import ConnectDBase

load_dotenv()


def create_errorDbase() -> None:

    # Safely read the last recorded serial number for
    if not os.path.exists(r".\TextFiles\last_recordedId.txt"):
        with open(r".\TextFiles\last_recordedId.txt", "w") as record_file:
            record_file.write("0")
        last_record_id = 0

    else:
        with open(r".\TextFiles\last_recordedId.txt", "r") as record_file:
            last_record_id = record_file.read()

    print(last_record_id)

    # Extract Application.evtx into json format
    powershell_command = (
        "Get-WinEvent -LogName Application | "
        f"Where-Object {{ $_.LevelDisplayName -in @('Error','Critical') -and $_.RecordId -gt {last_record_id} }} |"
        "Select-Object Id, LevelDisplayName, ProviderName, TimeCreated, Message, RecordId | "
        "ConvertTo-Json"
    )

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", powershell_command],
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

        with open(r".\TextFiles\last_recordedId.txt", "w") as record_file:
            record_file.write(str(max_record_id))

        con.disconnect_sql()

    # If `result` does not have values
    except json.decoder.JSONDecodeError:
        print("no field to append")

    finally:
        print("Successfully executed the program")

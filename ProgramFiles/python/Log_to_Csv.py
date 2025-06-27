import subprocess


class EventlogtoCSV:

    log_export_csv_path = "ProgramFiles\\powershell\\log_export_csv.ps1"
    list_event_sources_path = "ProgramFiles\\powershell\\list_event_sources.ps1"

    def __init__(self) -> None:
        list_command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            self.list_event_sources_path,
        ]
        try:
            subprocess.run(list_command, capture_output=True, text=True, check=True)
        except Exception:
            print("Failed to create the required txt file")

    def extract_evt_files(self, app_name: str):
        export_command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            self.log_export_csv_path,
            "-source",
        ]
        export_command.append(app_name)
        try:
            result = subprocess.run(
                export_command, capture_output=True, text=True, check=True
            )
            return result
        except Exception:
            print("Failed to create the required csv file")


if __name__ == "__main__":
    return_csv = EventlogtoCSV()
    return_csv.extract_evt_files(".NET Runtime")

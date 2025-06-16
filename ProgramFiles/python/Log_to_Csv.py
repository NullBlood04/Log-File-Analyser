import subprocess

class EventlogtoCSV:

    ps_script_path = "ProgramFiles\\powershell\\log_export_csv.ps1"
    
    def __init__(self, app_name: str) -> None:
        self.app_name = app_name
        self.command = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", self.ps_script_path,
        "-source", self.app_name
        ]


    def extract_evt_files(self):
        try:
            self.result = subprocess.run(self.command, capture_output=True, text=True, check=True)
            return self.result
        except Exception:
            print("Failed to create the required csv file")


if __name__ == "__main__":
    return_csv = EventlogtoCSV("Microsoft-Windows-Perflib")
    csv = return_csv.extract_evt_files()
    print(csv.stdout) # type: ignore
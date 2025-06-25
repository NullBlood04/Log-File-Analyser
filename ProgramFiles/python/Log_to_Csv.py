import subprocess

class EventlogtoCSV:

    ps_script_path = "ProgramFiles\\powershell\\log_export_csv.ps1"
    
    def __init__(self) -> None:
        self.command = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", self.ps_script_path,
        "-source"
        ]


    def extract_evt_files(self, app_name: str):
        self.command.append(app_name)
        try:
            result = subprocess.run(self.command, capture_output=True, text=True, check=True)
            return result
        except Exception:
            print("Failed to create the required csv file")

    
    """ def return_source(self):
        command = []
        return subprocess.run() """


if __name__ == "__main__":
    return_csv = EventlogtoCSV()
    csv = return_csv.extract_evt_files(".NET Runtime")
    #print(csv.stdout) # type: ignore
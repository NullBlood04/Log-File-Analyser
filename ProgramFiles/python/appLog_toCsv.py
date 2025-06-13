#import is_admin
#from dotenv import load_dotenv
#import os
#load_dotenv()
import subprocess



class LogtoCSV:

    ps_script_path = "..\\powershell\\log_export_csv.ps1"
    
    def __init__(self, app_name: str) -> None:
        self.app_name = app_name
        self.command = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", self.ps_script_path,
        "-source", self.app_name
        ]


    def extract_evt_files(self) -> subprocess.CompletedProcess:
        self.result = subprocess.run(self.command, capture_output=True, text=True, check=True)
        return self.result

""" 
if __name__ == "__main__":
    if is_admin.check_admin():
        FILE_PATH = os.getenv("FILE_PATH")
        app_log_filter = LogtoCSV(str(FILE_PATH)) """
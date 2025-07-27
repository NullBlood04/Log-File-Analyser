import subprocess
import logging
import os


from .. import PROJECT_ROOT

POWERSHELL_SCRIPT_PATH = os.path.join(
    PROJECT_ROOT, "ProgramFiles", "powershell", "extract_logs.ps1"
)


def _run_powershell_script(log_name: str, last_record_id: int) -> str | None:
    """Executes the PowerShell script to extract logs and returns the JSON output."""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                POWERSHELL_SCRIPT_PATH,
                str(last_record_id),
                log_name,
            ],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout
    except FileNotFoundError:
        logging.error(f"PowerShell script not found at {POWERSHELL_SCRIPT_PATH}")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"PowerShell script failed with error: {e.stderr}")
        return None

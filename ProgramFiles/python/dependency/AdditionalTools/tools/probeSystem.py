from langchain.tools import tool
import re
from subprocess import run
import logging

# A comprehensive whitelist of safe, read-only PowerShell commands
# with corresponding regex patterns for validation.
# This is defined once at the module level for efficiency.
ALLOWED_COMMANDS = {
    # --- System Information ---
    "Get-ComputerInfo": r"Get-ComputerInfo(?: \| Select-Object [\w,]+)?",
    "Get-CimInstance": r"Get-CimInstance -ClassName Win32_\w+",
    "Get-TimeZone": r"Get-TimeZone",
    # --- Process and Service Status ---
    "Get-Process": r'Get-Process(?: -Name "[\w\.\-]+")?',
    "Get-Service": r'Get-Service(?: -Name "[\w\.\-]+")?',
    "Get-ScheduledTask": r'Get-ScheduledTask(?: -TaskName "[\w\s\\-]+")?',
    # --- Event Logs and Diagnostics ---
    "Get-WinEvent_Filtered": r'Get-WinEvent -LogName Application -MaxEvents \d+ -FilterScript \{ \$\_.ProviderName -eq "[^"]+" -and \$\_.ID -eq \d+ \}',
    "Get-WinEvent_General": r"Get-WinEvent -LogName \w+ -MaxEvents \d+",
    # --- File System and Registry ---
    "Test-Path": r'Test-Path -Path "[\w\s\:\\\.\-]+"',
    "Get-ChildItem": r'Get-ChildItem -Path "[\w\s\:\\\.\-]+"',
    "Get-Content": r'Get-Content -Path "[\w\s\:\\\.\-]+\.\w+" -TotalCount \d+',
    "Get-ItemProperty": r'Get-ItemProperty -Path "HK[CL]M:[\w\s\\\:]+"',
    # --- Networking ---
    "Test-Connection": r'Test-Connection -ComputerName "[\w\.\-]+" -Count \d+',
    "Resolve-DnsName": r'Resolve-DnsName -Name "[\w\.\-]+"',
    "Get-NetIPAddress": r"Get-NetIPAddress(?: -AddressFamily (?:IPv4|IPv6))?",
    "Get-NetTCPConnection": r"Get-NetTCPConnection(?: -State \w+)?",
}


@tool(parse_docstring=True)
def probe_system(script: str) -> str:
    """
    Executes a read-only PowerShell script if it matches a command in a predefined security whitelist.
    This tool is for safely checking system status, not for making changes.

    Examples of allowed commands:
    - Get-Service -Name "Spooler"
    - Get-Process -Name "chrome"
    - Test-Path -Path "C:\\Users\\Public\\Documents"

    Args:
        script (str): Whitelisted PowerShell command to execute.

    Returns:
        str: Output from the executed script or an error message.
    """
    print("_________________probe_system used____________________")
    try:
        # Input Validation (Whitelist approach)
        command_found = False
        for pattern in ALLOWED_COMMANDS.values():
            if re.fullmatch(pattern, script):  # Use fullmatch for stricter validation
                command_found = True
                break

        if not command_found:
            raise ValueError("Script contains disallowed commands or invalid syntax.")

        result = run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=30,  # Timeout in seconds
            check=False,
        )

        output = result.stdout

        # Output Length Limiting
        max_output_length = 1024  # Example: Limit to 1024 characters
        if len(output) > max_output_length:
            output = output[:max_output_length] + "... (truncated)"

        if output:
            return output
        return "recieved no output from command"

    except Exception as e:
        logging.error(f"Error executing script: {e}")
        return f"Error: {str(e)}"

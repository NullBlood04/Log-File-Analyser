# Define script directory and CSV file path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$csvDir = Join-Path $scriptDir "..\..\CSV"
$csvPath = Join-Path $csvDir "ApplicationErrors.csv"

# Create CSV directory if it does not exist
If (!(Test-Path $csvDir)) {
    New-Item -ItemType Directory -Path $csvDir -Force
}

# Fetch Application log entries with Level Error or Critical
$logEntries = Get-WinEvent -LogName Application | Where-Object { $_.LevelDisplayName -in @("Error", "Critical") }

# Select relevant fields
$selectedEntries = $logEntries | Select-Object @{Name = "EventID"; Expression = { $_.Id } },
@{Name = "TimeCreated"; Expression = { $_.TimeCreated } },
@{Name = "Level"; Expression = { $_.LevelDisplayName } },
@{Name = "Source"; Expression = { $_.ProviderName } },
@{Name = "Message"; Expression = { $_.Message } }

# If CSV exists, import and merge while avoiding duplicates based on EventID and TimeCreated
If (Test-Path $csvPath) {
    $existing = Import-Csv $csvPath

    # Combine existing and new entries
    $combined = $existing + $selectedEntries

    # Remove duplicates based on EventID and TimeCreated
    $final = $combined | Sort-Object EventID, TimeCreated -Unique
}
Else {
    # No existing CSV, use current entries
    $final = $selectedEntries | Sort-Object EventID, TimeCreated
}

# Export to CSV
$final | Export-Csv -Path $csvPath -NoTypeInformation

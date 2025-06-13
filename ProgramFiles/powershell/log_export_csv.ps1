param(
    [string]$source
)

# --- Setup paths ---
$csvFolderRelative = "..\\CSVfiles"  # Relative path to the desired folder
$logFolderPath = Join-Path -Path $PSScriptRoot -ChildPath $csvFolderRelative

# Create Logs folder if it doesn't exist
if (-not (Test-Path $logFolderPath)) {
    New-Item -Path $logFolderPath -ItemType Directory | Out-Null
}

# File paths inside the Logs folder
$csvPath = Join-Path -Path $logFolderPath -ChildPath "AppErrorLogs.csv"
$lastIdPath = Join-Path -Path $logFolderPath -ChildPath "last_log_id.txt"

# --- Configuration ---
$logName = "Application"

# --- Get last processed Record ID ---
if (Test-Path $lastIdPath) {
    $lastRecordId = Get-Content $lastIdPath | Out-String | Trim
    $lastRecordId = [int]$lastRecordId
} else {
    $lastRecordId = 0
}

# --- Get new error logs with higher Record ID ---
$newLogs = Get-EventLog -LogName $logName -Source $source |
    Where-Object { $_.EntryType -eq "Error" -and $_.Index -gt $lastRecordId } |
    Sort-Object Index

# --- Export new logs if any ---
if ($newLogs.Count -gt 0) {
    $logData = $newLogs | Select-Object TimeGenerated, EntryType, Source, Message

    if (Test-Path $csvPath) {
        $logData | Export-Csv -Path $csvPath -NoTypeInformation -Append
    } else {
        $logData | Export-Csv -Path $csvPath -NoTypeInformation
    }

    # Save the latest Record ID for next run
    $latestRecordId = ($newLogs | Select-Object -Last 1).Index
    Set-Content -Path $lastIdPath -Value $latestRecordId
}

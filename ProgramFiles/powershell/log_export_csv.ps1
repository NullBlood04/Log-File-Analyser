param(
    [string]$source
)

# === Setup paths ===
$csvFolderRelative = "..\\..\\CSVfiles"
$logFolderPath = Join-Path -Path $PSScriptRoot -ChildPath $csvFolderRelative

# Create CSV folder if it doesn't exist
if (-not (Test-Path $logFolderPath)) {
    Write-Output "Creating CSV log folder at: $logFolderPath"
    New-Item -Path $logFolderPath -ItemType Directory | Out-Null
}

# Define file paths
$csvPath = Join-Path -Path $logFolderPath -ChildPath "AppErrorLogs.csv"
$lastIdPath = Join-Path -Path $logFolderPath -ChildPath "last_log_id.txt"
$logName = "Application"

# === Load last processed Record ID ===
if (Test-Path $lastIdPath) {
    $rawId = Get-Content $lastIdPath | Out-String | Trim
    Write-Output "Read raw Record ID from file: $rawId"
    
    try {
        $lastRecordId = [int]$rawId
    } catch {
        Write-Output "Failed to convert Record ID to int. Defaulting to 0."
        $lastRecordId = 0
    }
} else {
    Write-Output "No last_log_id.txt found. Starting fresh."
    $lastRecordId = 0
}

Write-Output "Log Source Provided: $source"
Write-Output "Last Processed Record ID: $lastRecordId"

# === Fetch new logs ===
$newLogs = Get-EventLog -LogName $logName -Source $source -ErrorAction SilentlyContinue |
    Where-Object { $_.EntryType -eq "Error" -and $_.Index -gt $lastRecordId } |
    Sort-Object Index

Write-Output "Found $($newLogs.Count) new error logs."

# === Export to CSV if new logs exist ===
if ($newLogs.Count -gt 0) {
    $logData = $newLogs | Select-Object TimeGenerated, EntryType, Source, EventID, Message

    if (Test-Path $csvPath) {
        Write-Output "Appending to existing CSV: $csvPath"
        $logData | Export-Csv -Path $csvPath -NoTypeInformation -Append
    } else {
        Write-Output "Creating new CSV: $csvPath"
        $logData | Export-Csv -Path $csvPath -NoTypeInformation
    }

    # Save latest Record ID
    $latestRecordId = ($newLogs | Select-Object -Last 1).Index
    Write-Output "Saving latest Record ID: $latestRecordId"
    Set-Content -Path $lastIdPath -Value $latestRecordId
} else {
    Write-Output "No new error logs to export."
}

param(
    [string]$source
)

# Setup paths
$csvFolderRelative = "..\\..\\CSVfiles"
$logFolderPath = Join-Path -Path $PSScriptRoot -ChildPath $csvFolderRelative

# Create folder if needed
if (-not (Test-Path $logFolderPath)) {
    Write-Output "Creating CSV log folder at: $logFolderPath"
    New-Item -Path $logFolderPath -ItemType Directory | Out-Null
}

$csvPath = Join-Path -Path $logFolderPath -ChildPath "AppErrorLogs.csv"
$lastIdPath = Join-Path -Path $logFolderPath -ChildPath "last_log_id.txt"
$logName = "Application"

# Read last index
if (Test-Path $lastIdPath) {
    $rawId = (Get-Content $lastIdPath -Raw).Trim()
    try {
        $lastIndex = [int]$rawId
    } catch {
        Write-Output "Invalid index in file. Resetting to 0."
        $lastIndex = 0
    }
} else {
    $lastIndex = 0
}

Write-Output "Log Source Provided: $source"
Write-Output "Last Processed Index: $lastIndex"

# Fetch new logs using Index
$newLogs = Get-EventLog -LogName $logName -Source $source -ErrorAction SilentlyContinue |
    Where-Object { $_.EntryType -eq "Error" -and $_.Index -gt $lastIndex } |
    Sort-Object Index

Write-Output "Found $($newLogs.Count) new error logs."

# Export if logs exist
if ($newLogs.Count -gt 0) {
    $logData = $newLogs | Select-Object Index, TimeGenerated, EntryType, Source, EventID, Message

    # Optional duplicate guard: compare Index values
    if (Test-Path $csvPath) {
        $existing = Import-Csv $csvPath
        $existingIndexes = $existing.Index

        $filteredData = $logData | Where-Object { $_.Index -notin $existingIndexes }
    } else {
        $filteredData = $logData
    }

    if ($filteredData.Count -gt 0) {
        Write-Output "Appending $($filteredData.Count) new logs to CSV."
        $filteredData | Export-Csv -Path $csvPath -NoTypeInformation -Append

        $latestIndex = ($filteredData | Select-Object -Last 1).Index
        Write-Output "Saving latest Index: $latestIndex"
        Set-Content -Path $lastIdPath -Value $latestIndex
    } else {
        Write-Output "No unique logs to append (already in CSV)."
    }
} else {
    Write-Output "No new logs found."
}

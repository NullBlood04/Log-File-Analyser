param(
    [string]$source
)

# --- Setup base path ---
$csvFolderRelative = "..\\..\\CSVfiles"
$baseFolderPath = Join-Path -Path $PSScriptRoot -ChildPath $csvFolderRelative

# Sanitize source name for safe folder/file naming
$sanitizedSource = ($source -replace '[\\/:*?"<>|]', '_')

# Create subfolder for this source under CSVfiles
$sourceFolderPath = Join-Path -Path $baseFolderPath -ChildPath $sanitizedSource

if (-not (Test-Path $sourceFolderPath)) {
    Write-Output "Creating folder for source at: $sourceFolderPath"
    New-Item -Path $sourceFolderPath -ItemType Directory | Out-Null
}

# Define source-specific paths
$csvPath = Join-Path -Path $sourceFolderPath -ChildPath "$sanitizedSource.csv"
$lastIdPath = Join-Path -Path $sourceFolderPath -ChildPath "$sanitizedSource`_last_log_id.txt"
$logName = "Application"

# Read last processed index (for incremental fetch)
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

Write-Output "`nProcessing logs for source: $source"
Write-Output "Last Processed Index: $lastIndex"

# Fetch new logs from the Application log
$newLogs = Get-EventLog -LogName $logName -Source $source -ErrorAction SilentlyContinue |
    Where-Object { $_.EntryType -eq "Error" -and $_.Index -gt $lastIndex } |
    Sort-Object Index

Write-Output "Found $($newLogs.Count) new error logs."

if ($newLogs.Count -gt 0) {
    # Select relevant fields
    $logData = $newLogs | Select-Object Index, TimeGenerated, EntryType, Source, EventID, Message

    # Clean message to remove newlines (for clean CSV rows)
    $logData = $logData | ForEach-Object {
        $_.Message = ($_.Message -replace '\r?\n', ' ')  # Replace newlines with space
        $_
    }

    # Check for duplicates if file exists
    if (Test-Path $csvPath) {
        $existing = Import-Csv $csvPath
        $existingIndexes = $existing.Index
        $filteredData = $logData | Where-Object { $_.Index -notin $existingIndexes }
    } else {
        $filteredData = $logData
    }

    if ($filteredData.Count -gt 0) {
        Write-Output "Appending $($filteredData.Count) new logs to $csvPath"
        $filteredData | Export-Csv -Path $csvPath -NoTypeInformation -Append

        # Save the latest index
        $latestIndex = ($filteredData | Select-Object -Last 1).Index
        Write-Output "Saving latest Index: $latestIndex"
        Set-Content -Path $lastIdPath -Value $latestIndex
    } else {
        Write-Output "No unique logs to append (already in CSV)."
    }
} else {
    Write-Output "No new logs found for source: $source"
}

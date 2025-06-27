# Get the directory of the current script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define the target folder and file path
$textFilesFolder = Join-Path $scriptDir "..\..\TextFiles"
$targetFile = Join-Path $textFilesFolder "ApplicationSources.txt"

# Create the folder if it does not exist
if (-not (Test-Path $textFilesFolder)) {
    New-Item -ItemType Directory -Path $textFilesFolder | Out-Null
}

# If file exists, read existing sources
$existingSources = @()
if (Test-Path $targetFile) {
    $existingSources = Get-Content $targetFile
}

# Get current sources from Application log efficiently
# Using -Unique and selecting only Source
$currentSources = Get-WinEvent -LogName Application -MaxEvents 5000 |
    Select-Object -ExpandProperty ProviderName |
    Sort-Object -Unique

# Check for new sources not in existing file
$newSources = $currentSources | Where-Object { $_ -notin $existingSources }

if ((Test-Path $targetFile) -and ($newSources.Count -eq 0)) {
    Write-Host "No new sources found. Script exiting."
    exit
}

# Combine existing and new sources, remove duplicates, sort, and export
$allSources = $existingSources + $newSources | Sort-Object -Unique

# Export to file
$allSources | Out-File -FilePath $targetFile -Encoding UTF8

Write-Host "Sources exported successfully to $targetFile"

param(
    $last_record_id,
    $log_name
)

Get-WinEvent -LogName $log_name | 
Where-Object { $_.LevelDisplayName -in @('Error','Critical') -and $_.RecordId -gt $last_record_id } |
Select-Object Id, LevelDisplayName, ProviderName, TimeCreated, Message, RecordId | 
ConvertTo-Json
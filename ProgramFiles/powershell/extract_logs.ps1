param(
    $last_record_id
)

Get-WinEvent -LogName Application | 
Where-Object { $_.LevelDisplayName -in @('Error','Critical') -and $_.RecordId -gt $last_record_id } |
Select-Object Id, LevelDisplayName, ProviderName, TimeCreated, Message, RecordId | 
ConvertTo-Json
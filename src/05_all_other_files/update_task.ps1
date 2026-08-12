$taskName = "Antigravity_Fleet_Supervisor"
$t1 = New-ScheduledTaskTrigger -Daily -At "8:00AM"
$t2 = New-ScheduledTaskTrigger -AtLogon
Set-ScheduledTask -TaskName $taskName -Trigger $t1, $t2
Write-Output "Successfully updated triggers for $taskName"

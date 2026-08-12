# register_tqqq_task.ps1
# This script registers the TQQQ Master Engine Supervisor to run on system startup.
# The supervisor keeps the bot alive through market hours and crashes.

$TaskName = "Antigravity_TQQQ_Master"
$ActionPath = "python.exe"
$ActionArgs = (Join-Path $PSScriptRoot "tqqq_supervisor.py")
$WorkingDirectory = $PSScriptRoot

# Clean up existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing scheduled task: $TaskName"
}

# Create new action
$Action = New-ScheduledTaskAction -Execute $ActionPath -Argument "`"$ActionArgs`"" -WorkingDirectory $WorkingDirectory

# Create trigger: At Startup
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Important: Wake the computer to run this task
$Settings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Executes the TQQQ Master Engine Supervisor in a resilient loop."

Write-Host "Successfully registered scheduled task: $TaskName"
Write-Host "Task is scheduled to run at system startup. The supervisor will keep the intraday bot running."

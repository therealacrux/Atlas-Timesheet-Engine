param(
	[string]$TaskName = "AtlasTimesheetDaily",
	[string]$ProjectRoot = "$PSScriptRoot\..",
	[string]$OneNoteRecipient = "me@onenote.com",
	[string]$PythonPath = "python",
	[string]$RawPath = "$PSScriptRoot\..\examples\raw.txt",
	[string]$OutputPath = "$PSScriptRoot\..\examples\output.txt",
	[string]$DefaultClient = "KOBOLD",
	[bool]$UseModel = $false,
	[string]$Model = "gpt-4o-mini",
	[string]$RunTime = "19:00" # 24h format, local time
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $ProjectRoot "scripts/schedule_timesheet.ps1"
if (-not (Test-Path -LiteralPath $scriptPath)) {
	throw "Cannot find schedule_timesheet.ps1 at $scriptPath"
}

# Build argument list for the scheduled script
$psArgs = @(
	"-ExecutionPolicy", "Bypass",
	"-NoProfile",
	"-File", "`"$scriptPath`"",
	"-PythonPath", "`"$PythonPath`"",
	"-ProjectRoot", "`"$ProjectRoot`"",
	"-RawPath", "`"$RawPath`"",
	"-OutputPath", "`"$OutputPath`"",
	"-DefaultClient", "`"$DefaultClient`"",
	"-OneNoteRecipient", "`"$OneNoteRecipient`""
)
if ($UseModel) {
	$psArgs += @("-UseModel:$true", "-Model", "`"$Model`"")
}
$argString = $psArgs -join ' '

# Create trigger at $RunTime daily (local time)
$time = [DateTime]::ParseExact($RunTime, "HH:mm", $null)
$trigger = New-ScheduledTaskTrigger -Daily -At $time

# Run as current user
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory $ProjectRoot

# Register (replace if exists)
try {
	Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
} catch {}

Register-ScheduledTask -TaskName $TaskName -Trigger $trigger -Action $action -Description "Run Atlas Timesheet Engine daily" | Out-Null

Write-Host "Scheduled task '$TaskName' registered to run daily at $RunTime (local time)."

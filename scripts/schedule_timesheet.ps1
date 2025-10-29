param(
	[string]$PythonPath = "python",
	[string]$ProjectRoot = "$PSScriptRoot\..",
	[string]$RawPath = "$PSScriptRoot\..\examples\raw.txt",
	[string]$OutputPath = "$PSScriptRoot\..\examples\output.txt",
	[string]$DefaultClient = "KOBOLD",
	[switch]$UseModel = $false,
	[string]$Model = "gpt-4o-mini",
	[string]$PromptPath = "$PSScriptRoot\..\prompt\timesheet_engine_prompt.md",
	[string]$OneNoteRecipient = "me@onenote.com",
	[switch]$UseOneNoteCom = $false,
	[string]$SectionId = ""
)

$ErrorActionPreference = "Stop"

# Ensure raw file exists
if (-not (Test-Path -LiteralPath $RawPath)) {
	New-Item -ItemType File -Path $RawPath -Force | Out-Null
}

# Read raw content
$raw = Get-Content -LiteralPath $RawPath -Raw -ErrorAction SilentlyContinue
if ([string]::IsNullOrWhiteSpace($raw)) {
	Write-Host "No raw content found. Exiting."
	exit 0
}

# Build CLI args
$cli = Join-Path $ProjectRoot "cli/timesheet_rewriter.py"
if (-not (Test-Path -LiteralPath $cli)) {
	throw "Cannot find CLI at $cli"
}

$commonArgs = @("$cli", "$RawPath", "--out", "$OutputPath", "--default-client", "$DefaultClient")
if ($UseModel) {
	$commonArgs += @("--model", $Model, "--prompt", $PromptPath)
}

# Run CLI
Write-Host "Running Timesheet Engine..."
$pythonArgs = $commonArgs -join ' '
$proc = Start-Process -FilePath $PythonPath -ArgumentList $pythonArgs -NoNewWindow -PassThru -Wait
if ($proc.ExitCode -ne 0) {
	throw "Timesheet Engine failed with exit code $($proc.ExitCode)"
}

# Read output
$outText = Get-Content -LiteralPath $OutputPath -Raw -ErrorAction SilentlyContinue
if ([string]::IsNullOrWhiteSpace($outText)) {
	Write-Host "No output generated. Exiting."
	exit 0
}

$delivered = $false
if ($UseOneNoteCom) {
	try {
		if (-not $SectionId) { throw "-SectionId is required when -UseOneNoteCom is set." }
		Write-Host "Creating OneNote page via OneNote COM..."
		$sendScript = Join-Path $ProjectRoot "scripts/send_to_onenote.ps1"
		if (-not (Test-Path -LiteralPath $sendScript)) { throw "Cannot find $sendScript" }
		& powershell -STA -ExecutionPolicy Bypass -NoProfile -File $sendScript -SectionId $SectionId -Title "Timesheet $(Get-Date -Format 'yyyy-MM-dd')" -Content $outText
		$delivered = $true
	} catch {
		Write-Warning "OneNote COM failed: $($_.Exception.Message). Falling back to Outlook email path."
	}
}

if (-not $delivered) {
	Write-Host "Sending to OneNote via Outlook..."
	$outlook = New-Object -ComObject Outlook.Application
	$mail = $outlook.CreateItem(0)
	$mail.To = $OneNoteRecipient
	$mail.Subject = "Timesheet $(Get-Date -Format 'yyyy-MM-dd')"
	$mail.Body = $outText
	$mail.Send()
	$delivered = $true
}

# Clear raw file after successful send
if ($delivered) {
	Set-Content -LiteralPath $RawPath -Value "" -NoNewline
	Write-Host "Done. Entries sent and raw cleared."
}

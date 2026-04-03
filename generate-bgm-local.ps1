param(
    [string]$PromptFile = (Join-Path $PSScriptRoot "prompts\arcade-loop.txt"),
    [string]$Out = (Join-Path $PSScriptRoot "music\bgm-loop.wav"),
    [int]$Seconds = 30,
    [string]$Model = "facebook/musicgen-small",
    [Nullable[int]]$Seed = $null
)

$skillRoot = Join-Path $PSScriptRoot "skill"
$pythonExe = Join-Path $skillRoot ".venv\Scripts\python.exe"
$scriptPath = Join-Path $skillRoot "scripts\generate_music.py"

if (-not (Test-Path $pythonExe)) {
    throw "MusicGen skill environment is not set up. Run .\\setup-musicgen-local.ps1 first."
}

if (-not (Test-Path $scriptPath)) {
    throw "MusicGen skill script was not found at $scriptPath"
}

$arguments = @(
    "`"$scriptPath`"",
    "--prompt-file", $PromptFile,
    "--out", $Out,
    "--seconds", $Seconds,
    "--model", $Model
)

if ($Seed -ne $null) {
    $arguments += @("--seed", $Seed)
}

$stdoutPath = Join-Path $env:TEMP "musicgen-local-stdout.log"
$stderrPath = Join-Path $env:TEMP "musicgen-local-stderr.log"
$argumentString = ($arguments | ForEach-Object {
    if ($_ -match '\s') { "`"$_`"" } else { "$_" }
}) -join " "

$process = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList $argumentString `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -NoNewWindow `
    -PassThru

$startTime = Get-Date
$estimatedSeconds = [Math]::Max(20, [Math]::Ceiling($Seconds * 4.5))

while (-not $process.HasExited) {
    $elapsedSeconds = [int]((Get-Date) - $startTime).TotalSeconds
    $percent = [Math]::Min(92, [Math]::Max(5, [int](($elapsedSeconds / $estimatedSeconds) * 100)))
    Write-Progress `
        -Id 1 `
        -Activity "Generating local game music" `
        -Status "Elapsed ${elapsedSeconds}s, estimated ${estimatedSeconds}s. The estimate is approximate on CPU." `
        -PercentComplete $percent
    Start-Sleep -Seconds 1
}

$process.WaitForExit()
Write-Progress -Id 1 -Activity "Generating local game music" -Completed

$stdout = if (Test-Path $stdoutPath) { Get-Content -Raw $stdoutPath } else { "" }
$stderr = if (Test-Path $stderrPath) { Get-Content -Raw $stderrPath } else { "" }
$outputSucceeded = $false

if (Test-Path $Out) {
    $outFile = Get-Item $Out
    $outputSucceeded = $outFile.LastWriteTime -ge $startTime.AddSeconds(-1)
}

if ($stdout) {
    Write-Output $stdout.TrimEnd()
}

if (-not $outputSucceeded) {
    if ($stderr) {
        Write-Error $stderr.TrimEnd()
    }

    throw "Music generation did not produce the expected output file: $Out"
}

if ($stderr) {
    Write-Warning $stderr.TrimEnd()
}

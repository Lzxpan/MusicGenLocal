param()

$skillRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $skillRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    py -3 -m venv $venvPath
}

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

Write-Output "MusicGen 本機環境已完成：$pythonExe"

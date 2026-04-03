param()

$repoRoot = $PSScriptRoot
$exePath = Join-Path $repoRoot "dist\MusicGenLocal-Studio.exe"
$skillRoot = Join-Path $repoRoot "skill"
$venvPython = Join-Path $skillRoot ".venv\Scripts\python.exe"

if (Test-Path $exePath) {
    & $exePath
    return
}

if (-not (Test-Path $venvPython)) {
    throw "尚未建立 MusicGen 本機環境，請先執行 .\\setup-musicgen-local.ps1。"
}

Push-Location $repoRoot
try {
    & $venvPython -m app.main
}
finally {
    Pop-Location
}

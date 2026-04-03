param()

$skillRoot = Join-Path $PSScriptRoot "skill"
$setupScript = Join-Path $skillRoot "scripts\setup_venv.ps1"

if (-not (Test-Path $setupScript)) {
    throw "MusicGen skill setup script was not found at $setupScript"
}

& $setupScript

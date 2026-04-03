param()

$skillRoot = Join-Path $PSScriptRoot "skill"
$setupScript = Join-Path $skillRoot "scripts\setup_venv.ps1"

if (-not (Test-Path $setupScript)) {
    throw "找不到 MusicGen 環境安裝腳本：$setupScript"
}

& $setupScript

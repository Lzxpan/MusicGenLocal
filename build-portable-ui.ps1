param()

$repoRoot = $PSScriptRoot
$pythonExe = Join-Path $repoRoot "skill\.venv\Scripts\python.exe"
$specPath = Join-Path $repoRoot "musicgenlocal-ui.spec"

if (-not (Test-Path $pythonExe)) {
    throw "尚未建立 MusicGen 本機環境，請先執行 .\\setup-musicgen-local.ps1。"
}

if (-not (Test-Path $specPath)) {
    throw "找不到打包設定檔：$specPath"
}

Push-Location $repoRoot
try {
    & $pythonExe -m PyInstaller --noconfirm --clean $specPath
}
finally {
    Pop-Location
}

Write-Output "單檔 exe 打包完成：$repoRoot\\dist\\MusicGenLocal-Studio.exe"

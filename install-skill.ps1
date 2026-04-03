param(
    [switch]$Copy
)

$repoRoot = $PSScriptRoot
$targetSkillsRoot = Join-Path $env:USERPROFILE ".codex\skills"

New-Item -ItemType Directory -Force -Path $targetSkillsRoot | Out-Null

function Install-SkillFolder {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceFolder,
        [Parameter(Mandatory = $true)]
        [string]$SkillName
    )

    $sourceSkillPath = Join-Path $repoRoot $SourceFolder
    $targetSkillPath = Join-Path $targetSkillsRoot $SkillName

    if (-not (Test-Path $sourceSkillPath)) {
        throw "找不到 skill 來源資料夾：$sourceSkillPath"
    }

    if (Test-Path $targetSkillPath) {
        Write-Output "Skill 已存在，略過：$targetSkillPath"
        return
    }

    if ($Copy) {
        Copy-Item $sourceSkillPath $targetSkillPath -Recurse -Force
        Write-Output "已複製 skill 到 $targetSkillPath"
        return
    }

    New-Item -ItemType Junction -Path $targetSkillPath -Target $sourceSkillPath | Out-Null
    Write-Output "已建立 skill junction：$targetSkillPath -> $sourceSkillPath"
}

Install-SkillFolder -SourceFolder "skill" -SkillName "musicgen-local"
Install-SkillFolder -SourceFolder "skill-ui" -SkillName "musicgen-local-ui"

Write-Output "請重新啟動 Codex，讓新 skill 生效。"

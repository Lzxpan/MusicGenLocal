param(
    [switch]$Copy
)

$repoRoot = $PSScriptRoot
$sourceSkillPath = Join-Path $repoRoot "skill"
$targetSkillsRoot = Join-Path $env:USERPROFILE ".codex\skills"
$targetSkillPath = Join-Path $targetSkillsRoot "musicgen-local"

if (-not (Test-Path $sourceSkillPath)) {
    throw "Skill source folder was not found: $sourceSkillPath"
}

New-Item -ItemType Directory -Force -Path $targetSkillsRoot | Out-Null

if (Test-Path $targetSkillPath) {
    throw "Target skill path already exists: $targetSkillPath"
}

if ($Copy) {
    Copy-Item $sourceSkillPath $targetSkillPath -Recurse -Force
    Write-Output "Skill copied to $targetSkillPath"
}
else {
    New-Item -ItemType Junction -Path $targetSkillPath -Target $sourceSkillPath | Out-Null
    Write-Output "Skill junction created: $targetSkillPath -> $sourceSkillPath"
}

Write-Output "Restart Codex to pick up the new skill."

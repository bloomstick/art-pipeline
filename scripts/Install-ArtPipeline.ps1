<#
.SYNOPSIS
    Install the art-pipeline image-gen skill globally from this repo.
.DESCRIPTION
    Copies skills/image-gen/SKILL.md -> global OpenCode skills so any agent
    in any project loads the canonical workflow. Never touches machine
    state: models, venvs, servers and env vars are the owner's job per
    docs/MACHINE-SETUP.md (this script only CHECKS and reports).
    Re-run after skill edits. Restart OpenCode after install/update.
.EXAMPLE
    .\scripts\Install-ArtPipeline.ps1
#>
$ErrorActionPreference = "Stop"

$Repo = Split-Path (Split-Path $MyInvocation.MyCommand.Path -Parent) -Parent
$SkillSrc = (Join-Path $Repo "skills/image-gen/SKILL.md")
if (-not (Test-Path $SkillSrc -PathType Leaf)) { throw "skill source missing: $SkillSrc" }

$SkillDir = (Join-Path $env:USERPROFILE ".config/opencode/skills")
$Dst = (Join-Path $SkillDir "image-gen")
New-Item -ItemType Directory -Force $Dst | Out-Null
Copy-Item $SkillSrc (Join-Path $Dst "SKILL.md") -Force
Write-Output ("SKILL: installed -> {0}" -f (Join-Path $Dst "SKILL.md"))

$Missing = @()
foreach ($V in @('COMFY_URL', 'COMFY_INPUT', 'COMFY_DIR', 'COMFY_PYTHON', 'ART_VENV_PY', 'ART_PIPELINE_DIR', 'HF_HOME', 'ART_ESRGAN_MODEL')) {
  $Val = [System.Environment]::GetEnvironmentVariable($V, 'User')
  if ([string]::IsNullOrWhiteSpace($Val)) { $Missing += $V }
  else { Write-Output ("ENV: {0} = {1}" -f $V, $Val) }
}
if ($Missing.Count -gt 0) {
  Write-Output ("ENV-MISSING ({0}): {1}" -f $Missing.Count, ($Missing -join ', '))
  Write-Output "Set them per docs/MACHINE-SETUP.md (setx VAR value), then re-run to verify."
} else {
  Write-Output "ENV: all required variables present."
}

Write-Output "DONE: image-gen skill installed globally. Restart OpenCode, then use the skill for any anime generation task."

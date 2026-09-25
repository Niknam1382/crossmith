# Sets up the engine venv (if needed), drops a dev-mode sidecar wrapper so
# the Rust shell can spawn the engine the same way it will in production,
# and starts `tauri dev`. See scripts/dev.sh for why the wrapper approach
# is used instead of freezing a real binary on every run.
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$EngineDir = Join-Path $RepoRoot "engine"
$DesktopDir = Join-Path $RepoRoot "desktop"
$BinDir = Join-Path $DesktopDir "src-tauri\binaries"

Write-Host "==> Engine: virtualenv"
if (-not (Test-Path "$EngineDir\.venv")) {
    python -m venv "$EngineDir\.venv"
}
& "$EngineDir\.venv\Scripts\pip.exe" install --quiet -e $EngineDir

Write-Host "==> Engine: dev sidecar wrapper"
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$RustHostLine = (rustc -vV | Select-String "^host:")
if (-not $RustHostLine) {
    Write-Error "couldn't determine your Rust target triple (is Rust installed? see rustup.rs)"
    exit 1
}
$TargetTriple = $RustHostLine.ToString().Split(" ")[1].Trim()
$Wrapper = Join-Path $BinDir "crossmith-engine-$TargetTriple.cmd"
Set-Content -Path $Wrapper -Value "@echo off`r`n`"$EngineDir\.venv\Scripts\crossmith-engine.exe`" %*"
Write-Host "    wrote $Wrapper"

Write-Host "==> Starting Tauri dev shell"
Set-Location $DesktopDir
npm run tauri dev

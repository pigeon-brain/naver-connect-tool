[CmdletBinding()]
param([switch]$WithDeviceTools)
$ErrorActionPreference='Stop'
$repoRoot=Split-Path -Parent $PSScriptRoot
$python=Join-Path $repoRoot '.venv\Scripts\python.exe'
function Invoke-Checked {
 param([string]$Executable,[string[]]$Arguments)
 & $Executable @Arguments
 if($LASTEXITCODE -ne 0){throw "Command failed: $Executable (exit $LASTEXITCODE)"}
}
if(!(Test-Path -LiteralPath $python)){
 Invoke-Checked -Executable 'py' -Arguments @('-3','-m','venv',(Join-Path $repoRoot '.venv'))
}
Invoke-Checked -Executable $python -Arguments @('-m','pip','install','-r',(Join-Path $repoRoot 'requirements.txt'))
if($WithDeviceTools){
 $mtkRoot=Join-Path $repoRoot 'vendor\mtkclient'
 $commit='118a000a83ea31c4f427fe5225abfe964546e05e'
 if(!(Test-Path -LiteralPath $mtkRoot)){
  Invoke-Checked -Executable 'git' -Arguments @('clone','--no-checkout','https://github.com/bkerler/mtkclient.git',$mtkRoot)
  Invoke-Checked -Executable 'git' -Arguments @('-C',$mtkRoot,'checkout','--detach',$commit)
 }
 $head=(& git -C $mtkRoot rev-parse HEAD).Trim()
 if($LASTEXITCODE -ne 0 -or $head -ne $commit){throw 'Unexpected mtkclient revision. Existing checkout was not changed.'}
 $patchFile=Join-Path $repoRoot 'patches\mtkclient-118a000.patch'
 & git -C $mtkRoot apply --reverse --check $patchFile 2>$null
 if($LASTEXITCODE -ne 0){
  Invoke-Checked -Executable 'git' -Arguments @('-C',$mtkRoot,'apply','--check',$patchFile)
  Invoke-Checked -Executable 'git' -Arguments @('-C',$mtkRoot,'apply',$patchFile)
 }
 Invoke-Checked -Executable $python -Arguments @('-m','pip','install','-r',(Join-Path $mtkRoot 'requirements.txt'))
}
Write-Host 'Environment ready. Preview.cmd opens a device-safe preview.'
Write-Host 'Platform-Tools and mode-specific USB drivers must be installed separately.'

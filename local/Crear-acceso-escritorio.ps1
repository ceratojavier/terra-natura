$ErrorActionPreference = 'Stop'

$desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
$bAt = Join-Path $PSScriptRoot 'Abrir-Terra-Natura.bat'

if (-not (Test-Path -LiteralPath $bAt)) {
  Write-Error ('No esta Abrir-Terra-Natura.bat en: ' + $PSScriptRoot)
  exit 1
}

$repoRoot = Split-Path $PSScriptRoot -Parent
$lnkPath = Join-Path $desktop 'Terra Natura.lnk'

if (Test-Path -LiteralPath $lnkPath) { Remove-Item -LiteralPath $lnkPath -Force }

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnkPath)
$sc.TargetPath = $bAt
$sc.WorkingDirectory = $repoRoot
$sc.Description = 'Terra Natura — YouTube, calendario y videos editoriales'
$sc.WindowStyle = 1

$iconSvg = Join-Path $repoRoot 'frontend\public\assets\icons\app-icon.svg'
$iconIco = Join-Path $repoRoot 'frontend\public\assets\icons\app-icon.ico'
if (Test-Path -LiteralPath $iconIco) {
  $sc.IconLocation = $iconIco
} else {
  $sc.IconLocation = "$env:SystemRoot\System32\imageres.dll,184"
}

$sc.Save()

Write-Host ''
Write-Host 'Listo. Icono en el escritorio:' -ForegroundColor Green
Write-Host $lnkPath
Write-Host ''
Write-Host 'Doble clic abre Terra Natura (recolectar YouTube + videos editoriales).'
Write-Host 'Dejá abierta la ventana negra del servidor mientras usás el programa.'

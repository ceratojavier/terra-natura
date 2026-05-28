$root = (Resolve-Path "$PSScriptRoot\..").Path
$src = Join-Path $root "frontend\public\media"
$dstWeb = Join-Path $root "web\public\media"
$dst = Join-Path $root "frontend\public\media"
if (-not (Test-Path $src)) {
  Write-Warning "No existe frontend\public\media - copia fotos a web\public\media\galeria\"
  exit 0
}
foreach ($d in @($dst, $dstWeb)) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  Copy-Item -Path "$src\*" -Destination $d -Recurse -Force
}
Write-Host "OK: media copiada a frontend y web"

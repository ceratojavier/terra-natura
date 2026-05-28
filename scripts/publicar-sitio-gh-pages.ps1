# Publica SOLO frontend/public en la rama gh-pages (raíz del sitio).
# Uso: powershell -ExecutionPolicy Bypass -File scripts\publicar-sitio-gh-pages.ps1

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$src = Join-Path $repoRoot "frontend\public"
$branch = "gh-pages"
$tmp = Join-Path $env:TEMP "terra-natura-pages-deploy"

if (-not (Test-Path $src)) {
  Write-Error "No existe $src"
}

Write-Host "Copiando sitio desde frontend\public ..."
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null
Copy-Item -Path (Join-Path $src "*") -Destination $tmp -Recurse -Force

Push-Location $repoRoot
try {
  $current = git rev-parse --abbrev-ref HEAD
  git fetch origin $branch 2>$null

  if (git show-ref --verify --quiet "refs/heads/$branch") {
    git branch -D $branch 2>$null
  }

  git checkout --orphan $branch
  git rm -rf . 2>$null | Out-Null

  Copy-Item -Path (Join-Path $tmp "*") -Destination $repoRoot -Recurse -Force
  if (-not (Test-Path (Join-Path $repoRoot "CNAME"))) {
    Set-Content -Path (Join-Path $repoRoot "CNAME") -Value "alpinasterranatura.com.ar" -NoNewline
  }

  git add -A
  git commit -m "Publicar sitio web Terra Natura (frontend/public)"
  git push -f origin $branch

  Write-Host ""
  Write-Host "Listo. En 1-3 minutos debería actualizarse https://alpinasterranatura.com.ar"
}
finally {
  git checkout $current 2>$null
  if (-not $?) { git checkout main }
  Pop-Location
  if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
}

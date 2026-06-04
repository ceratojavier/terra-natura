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
Get-ChildItem $tmp -Recurse -Include *.db | Remove-Item -Force

$deploy = Join-Path $env:TEMP "terra-natura-ghpages-deploy"
if (Test-Path $deploy) { Remove-Item $deploy -Recurse -Force }
New-Item -ItemType Directory -Path $deploy | Out-Null
Copy-Item -Path (Join-Path $tmp "*") -Destination $deploy -Recurse -Force

Push-Location $deploy
try {
  $env:GIT_AUTHOR_NAME = "Terra Natura Deploy"
  $env:GIT_AUTHOR_EMAIL = "alpinasterranatura@gmail.com"
  $env:GIT_COMMITTER_NAME = $env:GIT_AUTHOR_NAME
  $env:GIT_COMMITTER_EMAIL = $env:GIT_AUTHOR_EMAIL

  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"

  git init | Out-Null
  git checkout -B $branch | Out-Null
  git add -A
  git diff --cached --quiet
  $needCommit = $LASTEXITCODE -ne 0
  if ($needCommit) {
    git commit -m "Publicar sitio web Terra Natura (cotizador + cache tarifas)"
  }
  $commitOk = $LASTEXITCODE -eq 0
  $hasOrigin = $false
  git remote get-url origin 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) {
    $hasOrigin = $true
    git remote remove origin | Out-Null
  }
  git remote add origin "https://github.com/ceratojavier/terra-natura.git"
  git push -f origin $branch
  $pushOk = $LASTEXITCODE -eq 0

  $ErrorActionPreference = $prevEap
  if ($needCommit -and -not $commitOk) { throw "git commit failed" }
  if (-not $pushOk) { throw "git push failed - check GitHub access" }

  Write-Host ""
  Write-Host "Listo. En 1-3 minutos debería actualizarse https://alpinasterranatura.com.ar"
}
finally {
  Pop-Location
  if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
}

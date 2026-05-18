$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$python = $null

if (Test-Path $bundledPython) {
  $python = $bundledPython
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $python = (Get-Command python).Source
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $python = (Get-Command py).Source
}

if (-not $python) {
  throw "No se encontro Python. Instala Python 3 o ejecuta el proyecto desde Codex."
}

$configPath = Join-Path $projectRoot "config.local.json"
if (Test-Path $configPath) {
  $config = Get-Content $configPath -Raw | ConvertFrom-Json
  $emailEnabled = $config.email.enabled -eq $true
  $needsSmtpPassword = $emailEnabled -and $config.email.smtp_user -and -not $config.email.smtp_password -and -not $env:PRIVATE_WEB_SMTP_PASSWORD

  if ($needsSmtpPassword) {
    $securePassword = Read-Host "Contraseña SMTP para $($config.email.smtp_user)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    try {
      $env:PRIVATE_WEB_SMTP_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    } finally {
      [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
  }
}

& $python (Join-Path $projectRoot "server.py")

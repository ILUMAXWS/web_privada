param(
  [switch]$NoPrompt
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$python = $null
$smtpSecretPath = Join-Path $projectRoot "secrets\smtp_password.dpapi"

function Set-PrivateWebSmtpPasswordFromSecureString {
  param(
    [Parameter(Mandatory = $true)]
    [Security.SecureString]$SecurePassword
  )

  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
  try {
    $env:PRIVATE_WEB_SMTP_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
  } finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
}

function Read-DpapiSecret {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  try {
    $encrypted = (Get-Content -Path $Path -Raw).Trim()
    $machinePrefix = "DPAPI-MACHINE:"

    if ($encrypted.StartsWith($machinePrefix)) {
      Add-Type -AssemblyName System.Security
      $protectedBytes = [Convert]::FromBase64String($encrypted.Substring($machinePrefix.Length))
      $plainBytes = [Security.Cryptography.ProtectedData]::Unprotect(
        $protectedBytes,
        $null,
        [Security.Cryptography.DataProtectionScope]::LocalMachine
      )

      try {
        $plainText = [Text.Encoding]::UTF8.GetString($plainBytes)
        return ConvertTo-SecureString $plainText -AsPlainText -Force
      } finally {
        [Array]::Clear($plainBytes, 0, $plainBytes.Length)
      }
    }

    return $encrypted | ConvertTo-SecureString
  } catch {
    throw "No se pudo leer el secreto SMTP cifrado en $Path. Vuelve a crearlo con tools\save_smtp_secret.ps1."
  }
}

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
    if (Test-Path $smtpSecretPath) {
      $securePassword = Read-DpapiSecret -Path $smtpSecretPath
      Set-PrivateWebSmtpPasswordFromSecureString -SecurePassword $securePassword
    } else {
      throw "PRIVATE_WEB_SMTP_PASSWORD no esta configurada y no existe secrets\smtp_password.dpapi. En produccion define la variable como secreto del servicio; en Windows local crea el secreto cifrado con tools\save_smtp_secret.ps1."
    }
  }
}

& $python (Join-Path $projectRoot "server.py")

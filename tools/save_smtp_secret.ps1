param(
  [string]$SecretPath
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $SecretPath) {
  $SecretPath = Join-Path $projectRoot "secrets\smtp_password.dpapi"
}

function ConvertTo-LocalMachineDpapiSecret {
  param(
    [Parameter(Mandatory = $true)]
    [Security.SecureString]$SecurePassword
  )

  Add-Type -AssemblyName System.Security

  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
  try {
    $plainText = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    $plainBytes = [Text.Encoding]::UTF8.GetBytes($plainText)

    try {
      $protectedBytes = [Security.Cryptography.ProtectedData]::Protect(
        $plainBytes,
        $null,
        [Security.Cryptography.DataProtectionScope]::LocalMachine
      )

      return "DPAPI-MACHINE:" + [Convert]::ToBase64String($protectedBytes)
    } finally {
      [Array]::Clear($plainBytes, 0, $plainBytes.Length)
    }
  } finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
}

$secretDir = Split-Path -Parent $SecretPath
New-Item -ItemType Directory -Path $secretDir -Force | Out-Null

$securePassword = Read-Host "Contrasena SMTP" -AsSecureString
$encrypted = ConvertTo-LocalMachineDpapiSecret -SecurePassword $securePassword
$encrypted | Set-Content -Path $SecretPath -Encoding UTF8 -NoNewline

Write-Host "Secreto SMTP guardado cifrado en $SecretPath"
Write-Host "El archivo esta cifrado con DPAPI de maquina local y esta ignorado por Git."

# Web privada

Web local con login de usuario y contrasena, sesiones firmadas con cookie HTTP-only y panel privado para gestionar usuarios.

## Arrancar

En PowerShell:

```powershell
.\start.ps1
```

Luego abre:

```text
http://127.0.0.1:8000
```

Configura el primer administrador en local con `tools/set_credentials.py` antes de usar la web en produccion.

## Gestion de usuarios

Entra como `admin` y abre la zona privada. Desde ahi puedes:

- Anadir usuarios.
- Asociar y actualizar el email de cada usuario.
- Asignar rol de usuario o administrador.
- Cambiar tu propia contrasena.
- Enviar emails de restablecimiento de contrasena.
- Activar, desactivar o eliminar cuentas.

Las contrasenas se guardan como hashes PBKDF2 en `config.local.json`; no se almacenan en texto plano.

## Recuperacion por email

En el login, usa `Has olvidado tu contrasena?`. La web pedira el email asociado al usuario y enviara un enlace valido durante 1 hora.

Para envio real, configura `email` en `config.local.json`:

```json
{
  "email": {
    "enabled": true,
    "smtp_host": "smtp.tudominio.com",
    "smtp_port": 587,
    "smtp_user": "usuario-smtp",
    "smtp_password": "",
    "from_email": "no-reply@ilumax.es",
    "from_name": "ILUMAX",
    "use_ssl": false,
    "use_tls": true
  }
}
```

Deja `smtp_password` vacio. `start.ps1` no pide contrasenas al arrancar: lee `PRIVATE_WEB_SMTP_PASSWORD` si existe o, en Windows local, el secreto cifrado `secrets\smtp_password.dpapi`.

Si necesitas crear o renovar ese secreto local, ejecuta una vez:

```powershell
.\tools\save_smtp_secret.ps1
```

El archivo queda cifrado con DPAPI de maquina local y esta ignorado por Git.

Si `enabled` esta en `false`, los emails se guardan como `.eml` en la carpeta `outbox/` para pruebas locales.

## Produccion

En produccion configura `PRIVATE_WEB_SMTP_PASSWORD` como secreto o variable de entorno del servidor y arranca con:

```powershell
.\start.ps1 -NoPrompt
```

Consulta `docs/PRODUCCION.md` para las variables necesarias y opciones de servicio persistente.

## Cambiar credenciales desde terminal

Con el servidor detenido, puedes actualizar o crear un administrador asi:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\tools\set_credentials.py nuevo_usuario nueva_contrasena --email usuario@dominio.com
```

Despues reinicia el servidor.

`config.local.json`, `secrets\` y `.env` estan en `.gitignore` para evitar publicar secretos por accidente.

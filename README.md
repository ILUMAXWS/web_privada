# Web privada

Web local con login de usuario y contraseña, sesiones firmadas con cookie HTTP-only y panel privado para gestionar usuarios.

## Arrancar

En PowerShell:

```powershell
.\start.ps1
```

Luego abre:

```text
http://127.0.0.1:8000
```

Configura el primer administrador en local con `tools/set_credentials.py` antes de usar la web en producción.

## Gestión de usuarios

Entra como `admin` y abre la zona privada. Desde ahí puedes:

- Añadir usuarios.
- Asociar y actualizar el email de cada usuario.
- Asignar rol de usuario o administrador.
- Cambiar tu propia contraseña.
- Enviar emails de restablecimiento de contraseña.
- Activar, desactivar o eliminar cuentas.

Las contraseñas se guardan como hashes PBKDF2 en `config.local.json`; no se almacenan en texto plano.

## Recuperación por email

En el login, usa `¿Has olvidado tu contraseña?`. La web pedirá el email asociado al usuario y enviará un enlace válido durante 1 hora.

Para envío real, configura `email` en `config.local.json`:

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

Deja `smtp_password` vacío. `start.ps1` pedirá la contraseña SMTP en oculto al arrancar y la pasará al servidor solo como variable de entorno de esa sesión.

Si `enabled` está en `false`, los emails se guardan como `.eml` en la carpeta `outbox/` para pruebas locales.

## Cambiar credenciales desde terminal

Con el servidor detenido, puedes actualizar o crear un administrador así:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\tools\set_credentials.py nuevo_usuario nueva_contraseña --email usuario@dominio.com
```

Después reinicia el servidor.

`config.local.json` está en `.gitignore` para evitar publicar secretos por accidente.

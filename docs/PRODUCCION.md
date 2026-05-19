# Produccion

En produccion el servidor no debe pedir la contrasena SMTP por consola. La clave debe estar configurada como variable de entorno o secreto del proveedor donde se ejecute la web.

## Variables necesarias

Configura estas variables en el servicio, panel de hosting, contenedor o gestor de procesos:

```text
PRIVATE_WEB_EMAIL_ENABLED=true
PRIVATE_WEB_SMTP_HOST=mail.ilumax.es
PRIVATE_WEB_SMTP_PORT=587
PRIVATE_WEB_SMTP_USER=iws@ilumax.es
PRIVATE_WEB_SMTP_PASSWORD=<secreto-smtp>
PRIVATE_WEB_FROM_EMAIL=iws@ilumax.es
PRIVATE_WEB_FROM_NAME=ILUMAX
PRIVATE_WEB_SMTP_SSL=false
PRIVATE_WEB_SMTP_TLS=true
PRIVATE_WEB_SMTP_TLS_VERIFY=true
```

Tambien es recomendable definir:

```text
PRIVATE_WEB_SESSION_SECRET=<clave-larga-aleatoria>
HOST=127.0.0.1
PORT=8000
```

## Arranque sin prompts

Usa el modo sin prompt para servicios:

```powershell
.\start.ps1 -NoPrompt
```

Si falta `PRIVATE_WEB_SMTP_PASSWORD`, el proceso fallara al arrancar en vez de quedarse esperando teclado. Esto es intencionado para produccion.

## Persistencia del servicio

Ejecuta la web con un gestor de procesos que reinicie el servidor si se cae:

- Linux: `systemd`, Docker Compose o el gestor del proveedor cloud.
- Windows Server: servicio de Windows, IIS como proxy inverso, Task Scheduler al inicio, o un supervisor como NSSM.
- Hosting gestionado: configura las variables anteriores en el panel de secretos/variables de entorno.

La contrasena SMTP no debe guardarse en `config.local.json` ni subirse a GitHub. El proceso necesita leerla en tiempo de ejecucion, pero debe venir del sistema de secretos del servidor.

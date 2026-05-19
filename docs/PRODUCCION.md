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

El arranque no pide contrasenas por consola. El orden de lectura es:

1. `PRIVATE_WEB_SMTP_PASSWORD`, recomendado en produccion.
2. `secrets\smtp_password.dpapi`, valido para ejecucion local en Windows en la misma maquina.

Si no existe ninguno de los dos, el proceso falla al arrancar en vez de quedarse esperando teclado. Esto evita servicios colgados.

## Secreto local cifrado en Windows

Para un entorno local Windows puedes guardar el secreto una sola vez con:

```powershell
.\tools\save_smtp_secret.ps1
```

El archivo `secrets\smtp_password.dpapi` queda cifrado con DPAPI de maquina local y esta ignorado por Git. Para produccion sigue siendo preferible usar secretos o variables de entorno del proveedor.

## Persistencia del servicio

Ejecuta la web con un gestor de procesos que reinicie el servidor si se cae:

- Linux: `systemd`, Docker Compose o el gestor del proveedor cloud.
- Windows Server: servicio de Windows, IIS como proxy inverso, Task Scheduler al inicio, o un supervisor como NSSM.
- Hosting gestionado: configura las variables anteriores en el panel de secretos/variables de entorno.

La contrasena SMTP no debe guardarse en `config.local.json` ni subirse a GitHub. El proceso necesita leerla en tiempo de ejecucion, pero debe venir del sistema de secretos del servidor o de un secreto local cifrado.

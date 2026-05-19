from __future__ import annotations

from getpass import getpass
from pathlib import Path
import argparse
import base64
import hashlib
import json
import re
import secrets
import time


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.local.json"
ITERATIONS = 240_000
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return (
        f"pbkdf2_sha256${ITERATIONS}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(digest).decode('ascii')}"
    )


def load_existing_config() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8-sig") as handle:
            config = json.load(handle)
    else:
        config = {}

    if "users" in config:
        config.setdefault("email", {
            "enabled": False,
            "smtp_host": "",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_password": "",
            "from_email": "no-reply@ilumax.es",
            "from_name": "ILUMAX",
            "use_tls": True,
        })
        config.setdefault("reset_tokens", {})
        return config

    username = config.get("username", "admin")
    old_hash = config.get("password_hash", "")
    return {
        "session_secret": config.get("session_secret") or secrets.token_urlsafe(32),
        "email": {
            "enabled": False,
            "smtp_host": "",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_password": "",
            "from_email": "no-reply@ilumax.es",
            "from_name": "ILUMAX",
            "use_tls": True,
        },
        "reset_tokens": {},
        "users": {
            username: {
                "password_hash": old_hash,
                "email": f"{username}@ilumax.local",
                "role": "admin",
                "active": True,
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Actualiza o crea un usuario administrador.")
    parser.add_argument("username", nargs="?", help="Usuario")
    parser.add_argument("password", nargs="?", help="Contrasena")
    parser.add_argument("--email", help="Email asociado al usuario")
    args = parser.parse_args()

    username = args.username or input("Usuario: ").strip()
    password = args.password or getpass("Contrasena: ")
    email = args.email or input("Email: ").strip()

    if not username:
        raise SystemExit("El usuario no puede estar vacio.")
    if not EMAIL_PATTERN.fullmatch(email):
        raise SystemExit("Introduce un email valido.")
    if len(password) < 10:
        raise SystemExit("Usa una contrasena de al menos 10 caracteres.")

    config = load_existing_config()
    config["session_secret"] = config.get("session_secret") or secrets.token_urlsafe(32)
    config.setdefault("users", {})
    config.setdefault("email", {})["smtp_password"] = ""

    now = int(time.time())
    existing = config["users"].get(username, {})
    config["users"][username] = {
        "password_hash": password_hash(password),
        "email": email,
        "role": existing.get("role", "admin"),
        "active": bool(existing.get("active", True)),
        "created_at": int(existing.get("created_at", now)),
        "updated_at": now,
    }

    with CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Credenciales actualizadas en {CONFIG_PATH}")


if __name__ == "__main__":
    main()

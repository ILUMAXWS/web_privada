from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.local.json"


def remove_utf8_bom(path: Path) -> None:
    if not path.exists():
        return

    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        path.write_bytes(raw[3:])


remove_utf8_bom(CONFIG_PATH)
sys.path.insert(0, str(ROOT))

import server as server_module  # noqa: E402


server_namespace = getattr(server_module, "_namespace", server_module.__dict__)
config = server_namespace["CONFIG"]
config_path = server_namespace["CONFIG_PATH"]
alert_html = server_namespace["alert_html"]
create_session = server_namespace["create_session"]
find_username = server_namespace["find_username"]
find_username_by_email = server_namespace["find_username_by_email"]
render_page = server_namespace["render_page"]
urlencode = server_namespace["urlencode"]
verify_password_hash = server_namespace["verify_password_hash"]
HTTPStatus = server_namespace["HTTPStatus"]
LOGO_HTML = server_namespace["LOGO_HTML"]
SESSION_COOKIE = server_namespace["SESSION_COOKIE"]
SESSION_MAX_AGE_SECONDS = server_namespace["SESSION_MAX_AGE_SECONDS"]
PrivateWebHandler = server_namespace["PrivateWebHandler"]


def save_config_without_smtp_password() -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = config_path.with_suffix(".tmp")
    persisted_config = json.loads(json.dumps(config))
    persisted_config.setdefault("email", {})["smtp_password"] = ""

    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(persisted_config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    temp_path.replace(config_path)


def login_page_with_email(error: str | None = None, notice: str | None = None) -> tuple[int, bytes]:
    return render_page(
        "Acceso privado",
        f"""
<main class="login-shell">
  <section class="login-panel" aria-labelledby="login-eyebrow">
    {LOGO_HTML}
    <p class="eyebrow" id="login-eyebrow">&Aacute;rea privada</p>
    {alert_html(notice=notice or "", error=error or "")}
    <form method="post" action="/login" class="login-form">
      <label for="username">Usuario o email</label>
      <input id="username" name="username" type="text" autocomplete="username" required autofocus>

      <label for="password">Contrase&ntilde;a</label>
      <input id="password" name="password" type="password" autocomplete="current-password" required>

      <button type="submit">Entrar</button>
    </form>
    <p class="login-helper"><a href="/recuperar-contrasena">&iquest;Has olvidado tu contrase&ntilde;a?</a></p>
  </section>
</main>
""",
    )


def handle_login_with_email(self) -> None:
    form = self.read_form()
    requested_username = self.form_value(form, "username").strip()
    password = self.form_value(form, "password")
    existing_username = find_username(requested_username) or find_username_by_email(requested_username)
    user = config["users"].get(existing_username) if existing_username else None

    if (
        existing_username
        and user
        and user.get("active")
        and verify_password_hash(password, user.get("password_hash", ""))
    ):
        token = create_session(existing_username)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/privado")
        self.send_header(
            "Set-Cookie",
            (
                f"{SESSION_COOKIE}={token}; Max-Age={SESSION_MAX_AGE_SECONDS}; "
                "Path=/; HttpOnly; SameSite=Lax"
            ),
        )
        self.end_headers()
        return

    self.redirect("/login?" + urlencode({"error": "bad_login"}))


server_namespace["save_config"] = save_config_without_smtp_password
server_namespace["login_page"] = login_page_with_email
PrivateWebHandler.handle_login = handle_login_with_email
server_namespace["main"]()

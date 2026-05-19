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


def save_config_without_smtp_password() -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = config_path.with_suffix(".tmp")
    persisted_config = json.loads(json.dumps(config))
    persisted_config.setdefault("email", {})["smtp_password"] = ""

    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(persisted_config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    temp_path.replace(config_path)


server_namespace["save_config"] = save_config_without_smtp_password
server_namespace["main"]()

from __future__ import annotations

from pathlib import Path

from app.config_loader import load_config
from core.logger import setup_logging
from ui.qt_app import run_qt_app


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    setup_logging(root / "logs" / "app.log")
    cfg_path = root / "config" / "default.yaml"
    config = load_config(cfg_path)
    return run_qt_app(config)


if __name__ == "__main__":
    raise SystemExit(main())

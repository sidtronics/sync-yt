from .sync_yt import sync_all, parse_config
from pathlib import Path
import logging as log
import os


def main():

    log.basicConfig(
        format="[sync-yt] {levelname}: {message}",
        style="{",
        level=log.INFO,
    )

    if os.name == "posix":
        config_path = Path("~/.config/sync-yt/config.yaml").expanduser()
    elif os.name == "nt":
        config_path = Path(r"~\AppData\Local\sync-yt\config.yaml").expanduser()

    if not os.path.exists(config_path):
        config_path = Path("./config.yaml")

    config = parse_config(config_path)

    sync_dir = config.get("sync_dir")

    if not sync_dir:
        log.error("sync_dir not defined in config")
        exit(1)

    sync_dir = Path(sync_dir).expanduser()

    if not sync_dir.exists():
        log.error("sync_dir does not exist: %s", sync_dir)
        exit(1)

    sync_all(config)


if __name__ == "__main__":
    main()

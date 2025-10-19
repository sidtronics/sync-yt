from .sync_yt import sync_playlist, parse_config
from pathlib import Path
import os


def main():

    if os.name == "posix":
        default_path = Path("~/.config/sync-yt/config.json").expanduser()
    elif os.name == "nt":
        default_path = Path(r"~\AppData\Local\sync-yt\config.json").expanduser()

    if not os.path.exists(default_path):
        default_path = Path("./config.json")

    config = parse_config(default_path)

    sync_dir = Path(config["sync_dir"]).expanduser()
    if not os.path.exists(sync_dir):
        print(f"[sync-yt] ERROR: sync_dir does not exist ({sync_dir}).")
        exit(1)

    cookies_from_browser = config["cookies_from_browser"]

    for playlist in config["playlists"]:
        playlist_dir = os.path.join(sync_dir, playlist["name"])
        print(f'[sync-yt] INFO: Syncing: "{playlist["name"]}"')
        sync_playlist(
            playlist_dir,
            playlist["url"],
            playlist.get("convert_to_audio"),
            playlist.get("format"),
            cookies_from_browser,
        )
        print("-" * 50)

    print("[sync-yt] INFO: Finished Syncing")


if __name__ == "__main__":
    main()

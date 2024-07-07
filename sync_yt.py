from yt_dlp import YoutubeDL
from pathlib import Path

import json
import os
import re


def parse_rc(rc_path: Path):

    try:
        with open(rc_path, "r") as file:
            config = json.load(file)
    except json.JSONDecodeError as e:
        print(f"[sync-yt] ERROR: error while parsing \"{rc_path}\" : {e}")
        exit(1)
    except FileNotFoundError:
        print(f"[sync-yt] ERROR: file at \"{rc_path}\" does not exist.")
        exit(1)
    except Exception as e:
        print(f"[sync-yt] ERROR: An unexpected error occured: {e}")
    else:
        print(f"[sync-yt] INFO: Using config file: \"{rc_path}\"\n")
        return config


def remove_item(playlist_dir: Path, video_id: str):

    pattern = re.compile(fr".*\[{video_id}\]\..*")

    for file_name in os.listdir(playlist_dir):
        if pattern.match(file_name):
            print(f"[sync-yt] INFO: Removing: ID: \"{video_id}\"")
            os.remove(os.path.join(playlist_dir, file_name))
            break


def remove_from_archive(playlist_dir: Path, video_ids: list):

    if video_ids == []:
        return

    archive_path = os.path.join(playlist_dir, "archive.txt")

    archive = open(archive_path, "r")
    archive_records = archive.readlines()
    archive.close()

    for id in video_ids:
        try:
            archive_records.remove(f"youtube {id}\n")
        except ValueError:
            archive_records.remove(f"youtube {id}")

    archive = open(archive_path, "w")
    archive.writelines(archive_records)
    archive.close()


def get_playlist(playlist_url: str, cookies_from_browser: str = None):

    yt_dlp_args = {"extract_flat": "in_playlist", "quiet": True, "no_warnings": True}
    if cookies_from_browser is not None:
        yt_dlp_args["cookiesfrombrowser"] = (cookies_from_browser,)

    with YoutubeDL(yt_dlp_args) as ydl:
        info = ydl.extract_info(playlist_url)

    video_ids = set()
    for video in info["entries"] or []:
        video_ids.add(video["id"])
        if video["duration"] is None:
            print(f"[sync-yt] INFO: Unavailable video detected: ID: \"{video["id"]}\"")

    return video_ids


def get_archive(playlist_dir: Path):

    archive_path = Path(os.path.join(playlist_dir, "archive.txt"))

    return set(
        line[8:]
        for line in archive_path.read_text(encoding="utf8").splitlines()
        if line.startswith("youtube ")
    )


def download_yt(yt_dlp_args: dict, urls):

    with YoutubeDL(yt_dlp_args) as ydl:
        ydl.download(urls)


def sync_playlist(
    playlist_dir: Path,
    playlist_url: str,
    convert_to_audio: bool = False,
    cookies_from_browser: str = None,
):

    if not os.path.exists(playlist_dir):
        os.mkdir(playlist_dir)

    archive_path = os.path.join(playlist_dir, "archive.txt")
    playlist_name = os.path.basename(playlist_dir)

    yt_dlp_args = {
        "download_archive": archive_path,
        "paths": {"home": playlist_dir},
        'ignoreerrors': 'only_download',
        "quiet": True
    }

    if cookies_from_browser is not None:
        yt_dlp_args["cookiesfrombrowser"] = (cookies_from_browser,)
        # Workaround for a bug when downloading from private playlists:
        yt_dlp_args["extractor_args"] = {"youtube": {"player_client": ["ios"]}}

    if convert_to_audio:
        yt_dlp_args["format"] = "bestaudio/best"
        yt_dlp_args["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "best",
                "preferredquality": "5",
            }
        ]

    if not os.path.exists(archive_path):
        print(f"[sync-yt] INFO: Downloading new playlist at: \"{playlist_dir}\"")
        download_yt(yt_dlp_args, playlist_url)
        print(f"[sync-yt] INFO: Created: \"{playlist_name}/archive.txt\"")
        print(f"[sync-yt] INFO: Synced: \"{playlist_name}\"")
        return

    playlist_ids = get_playlist(playlist_url, cookies_from_browser)
    archive_ids = get_archive(playlist_dir)

    added_ids = playlist_ids - archive_ids
    removed_ids = archive_ids - playlist_ids

    if len(added_ids) == 0 and len(removed_ids) == 0:
        print(f"[sync-yt] INFO: \"{playlist_name}\" is up to date.")
        return

    # Adding new videos to local playlist:
    if not len(added_ids) == 0:
        for id in added_ids:
            print(f"[sync-yt] INFO: Downloading: ID: \"{id}\"")

        download_yt(yt_dlp_args, added_ids)

    # Removing videos from local playlist:
    if not len(removed_ids) == 0:
        for id in removed_ids:
            remove_item(playlist_dir, id)

        remove_from_archive(playlist_dir, removed_ids)

    print(f"[sync-yt] INFO: Updated: \"{playlist_name}/archive.txt\"")
    print(f"[sync-yt] INFO: Synced: \"{playlist_name}\"")


def main():

    if os.name == "posix":
        default_path = Path("~/.config/sync-yt/rc.json").expanduser()
    elif os.name == "nt":
        default_path = Path(r"~\AppData\Local\sync-yt\rc.json").expanduser()

    config = parse_rc(default_path)

    sync_dir = Path(config["sync_dir"]).expanduser()
    if not os.path.exists(sync_dir):
        print(f"[sync-yt] ERROR: sync_dir does not exist ({sync_dir}).")
        exit(1)

    cookies_from_browser = config["cookies_from_browser"]

    for playlist in config["playlists"]:
        playlist_dir = os.path.join(sync_dir, playlist["name"])
        print(f"[sync-yt] INFO: Syncing: \"{playlist["name"]}\"")
        sync_playlist(
            playlist_dir,
            playlist["url"],
            playlist["convert_to_audio"],
            cookies_from_browser,
        )
        print("-"*50)

    print("[sync-yt] INFO: Finished Syncing")


if __name__ == "__main__":
    main()

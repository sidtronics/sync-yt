from yt_dlp import YoutubeDL
from pathlib import Path

import json
import os
import re


def parse_rc(rc_path: Path = Path("~/.config/sync-yt/rc.json").expanduser()):

    try:
        with open(rc_path, "r") as file:
            config = json.load(file)
    except json.JSONDecodeError as e:
        print(f"[sync-yt] ERROR: error parsing {rc_path} : {e}")
        exit(1)
    except FileNotFoundError:
        print(f"[sync-yt] ERROR: file at {rc_path} does not exist.")
        exit(1)
    except Exception as e:
        print(f"[sync-yt] ERROR: An unexpected error occured: {e}")
    else:
        return config


def remove_video(playlist_dir: Path, video_id: str):

    pattern = re.compile(fr".*\[{video_id}\]\..*")

    for file_name in os.listdir(playlist_dir):
        if pattern.match(file_name):
            os.remove(os.path.join(playlist_dir, file_name))
            print(f"[sync-yt] INFO: Removed {file_name}")
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

    print(f"[sync-yt] INFO: Updated {os.path.basename(playlist_dir)}/archive.txt")


def get_playlist(playlist_url: str, cookiesfrombrowser: str = None):

    yt_dlp_args = {"extract_flat": "in_playlist", "quiet": True, "no_warnings": True}
    if cookiesfrombrowser is not None:
        yt_dlp_args["cookiesfrombrowser"] = (cookiesfrombrowser,)

    with YoutubeDL(yt_dlp_args) as ydl:
        info = ydl.extract_info(playlist_url)

    video_ids = set()
    for video in info["entries"] or []:
        video_ids.add(video["id"])
        if video["duration"] is None:
            print(f"[sync-yt] INFO: Unavailable video detected. ID: {video["id"]}")

    return video_ids


def get_archive(playlist_dir: Path):

    archive_path = Path(os.path.join(playlist_dir, "archive.txt"))

    return [
        line[8:]
        for line in archive_path.read_text(encoding="utf8").splitlines()
        if line.startswith("youtube ")
    ]


def sync_playlist(
    playlist_dir: Path,
    playlist_url: str,
    convert_to_audio: bool = False,
    cookiesfrombrowser: str = None,
):

    if not os.path.exists(playlist_dir):
        os.mkdir(playlist_dir)

    archive_path = os.path.join(playlist_dir, "archive.txt")

    yt_dlp_args = {
        "download_archive": archive_path,
        "paths": {"home": playlist_dir},
        "quiet": True,
    }

    if cookiesfrombrowser is not None:
        yt_dlp_args["cookiesfrombrowser"] = (cookiesfrombrowser,)
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

    with YoutubeDL(yt_dlp_args) as ydl:
        ydl.download(playlist_url)

    video_ids = get_playlist(playlist_url, cookiesfrombrowser)
    archive_ids = get_archive(playlist_dir)

    removed_ids = [id for id in archive_ids if id not in video_ids]

    for id in removed_ids:
        remove_video(playlist_dir, id)

    remove_from_archive(playlist_dir, removed_ids)


def main():

    if os.name == "posix":
        default_path = Path("~/.config/sync-yt/rc.json").expanduser()
    elif os.name == "nt":
        default_path = Path(r"~\AppData\Local\sync-yt\rc.json").expanduser()

    config = parse_rc(default_path)

    sync_dir = Path(config["sync_dir"]).expanduser()
    if not os.path.exists(sync_dir):
        print(f"[sync-yt] ERROR: sync_dir does not exist ({sync_dir}).")

    cookiesfrombrowser = config["cookies_from_browser"]

    for playlist in config["playlists"]:
        playlist_dir = os.path.join(sync_dir, playlist["name"])
        print(f'[sync-yt] INFO: Syncing playlist "{playlist["name"]}" ')
        sync_playlist(
            playlist_dir,
            playlist["url"],
            playlist["convert_to_audio"],
            cookiesfrombrowser,
        )


if __name__ == "__main__":
    main()

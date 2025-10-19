from yt_dlp import YoutubeDL
from pathlib import Path
import json
import os
import re


def parse_config(config_path: Path):

    try:
        with open(config_path, "r") as file:
            config = json.load(file)
    except json.JSONDecodeError as e:
        print(f'[sync-yt] ERROR: error while parsing "{config_path}" : {e}')
        exit(1)
    except FileNotFoundError:
        print(f'[sync-yt] ERROR: file at "{config_path}" does not exist.')
        exit(1)
    except Exception as e:
        print(f"[sync-yt] ERROR: An unexpected error occured: {e}")
    else:
        print(f'[sync-yt] INFO: Using config file: "{config_path}"\n')
        return config


def remove_item(playlist_dir: Path, video_id: str):

    pattern = re.compile(rf".*\[{video_id}\]\..*")

    for file_name in os.listdir(playlist_dir):
        if pattern.match(file_name):
            print(f'[sync-yt] INFO: Removing: ID: "{video_id}"')
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
            print(f'[sync-yt] INFO: Unavailable video detected: ID: "{video["id"]}"')

    return video_ids


def get_archive(playlist_dir: Path):

    archive_path = Path(os.path.join(playlist_dir, "archive.txt"))

    return set(
        line[8:]
        for line in archive_path.read_text(encoding="utf8").splitlines()
        if line.startswith("youtube ")
    )


def sync_playlist(
    playlist_dir: Path,
    playlist_url: str,
    convert_to_audio: bool = False,
    format: str = None,
    cookies_from_browser: str = None,
):

    if not os.path.exists(playlist_dir):
        os.mkdir(playlist_dir)

    archive_path = os.path.join(playlist_dir, "archive.txt")
    playlist_name = os.path.basename(playlist_dir)

    yt_dlp_args = {
        "download_archive": archive_path,
        "paths": {"home": playlist_dir},
        "ignoreerrors": "only_download",
        "quiet": True,
    }

    if cookies_from_browser is not None:
        yt_dlp_args["cookiesfrombrowser"] = (cookies_from_browser,)

    if convert_to_audio:

        yt_dlp_args["format"] = "bestaudio/best"
        preferred_codec = format or "best"

        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": preferred_codec,
                "preferredquality": "5",
            }
        ]

        # Embed metadata if compatible format
        if preferred_codec in {"mp3", "m4a", "flac", "opus", "ogg"}:
            postprocessors.append(
                {
                    "add_chapters": False,
                    "add_infojson": False,
                    "add_metadata": True,
                    "key": "FFmpegMetadata",
                }
            )

        # Embed thumbnail as a cover art if compatible format
        if preferred_codec in {"mp3", "m4a", "flac"}:
            postprocessors.append(
                {"key": "EmbedThumbnail", "already_have_thumbnail": False}
            )
            yt_dlp_args["outtmpl"] = {"pl_thumbnail": ""}
            yt_dlp_args["writethumbnail"] = True

        yt_dlp_args["postprocessors"] = postprocessors

    # if video
    else:

        if format in {"avi", "flv", "mkv", "mov", "mp4", "webm"}:

            yt_dlp_args["final_ext"] = format
            yt_dlp_args["merge_output_format"] = format

            yt_dlp_args["postprocessors"] = [
                {"key": "FFmpegVideoRemuxer", "preferedformat": format}
            ]

            if format == "mp4":
                yt_dlp_args["format_sort"] = [
                    "vcodec:h264",
                    "lang",
                    "quality",
                    "res",
                    "fps",
                    "hdr:12",
                    "acodec:aac",
                ]

        elif format:
            print(f'[sync-yt] WARN: Unsupported video format: "{format}"')

    if os.path.exists(archive_path):
        archive_ids = get_archive(playlist_dir)
    else:
        print(f'[sync-yt] INFO: Downloading new playlist at: "{playlist_dir}"')
        archive_ids = set()
        Path(archive_path).touch()
        print(f'[sync-yt] INFO: Created: "{playlist_name}/archive.txt"')

    playlist_ids = get_playlist(playlist_url, cookies_from_browser)

    added_ids = playlist_ids - archive_ids
    removed_ids = archive_ids - playlist_ids

    if len(added_ids) == 0 and len(removed_ids) == 0:
        print(f'[sync-yt] INFO: "{playlist_name}" is up to date.')
        return

    # Download new videos
    if added_ids:
        total = len(added_ids)
        print(f"[sync-yt] INFO: {total} new video(s) to download.")

    with YoutubeDL(yt_dlp_args) as ydl:
        for i, id in enumerate(added_ids, start=1):
            print(f'[sync-yt] INFO: Downloading ({i}/{total}): ID: "{id}"', flush=True)
            ydl.download(id)

    # Remove videos
    if removed_ids:
        for id in removed_ids:
            remove_item(playlist_dir, id)

        remove_from_archive(playlist_dir, removed_ids)

    print(f'[sync-yt] INFO: Updated: "{playlist_name}/archive.txt"')
    print(f'[sync-yt] INFO: Synced: "{playlist_name}"')

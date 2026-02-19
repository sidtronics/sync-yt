from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget
from pathlib import Path
import logging as log
import json
import os
import re


def parse_config(config_path: Path):

    try:
        with open(config_path, "r") as file:
            config = json.load(file)
    except json.JSONDecodeError as e:
        log.error('Error while parsing "%s" : %s', config_path, e)
        exit(1)
    except FileNotFoundError:
        log.error('File at "%s" does not exist.', config_path)
        exit(1)
    except Exception as e:
        log.error("An unexpected error occured: %s", e)
        exit(1)
    else:
        log.info('Using config file: "%s"\n', config_path)
        return config


def remove_item(playlist_dir: Path, video_id: str):

    pattern = re.compile(rf".*\[{video_id}\]\..*")

    for file_name in os.listdir(playlist_dir):
        if pattern.match(file_name):
            log.info('Removing: ID: "%s"', video_id)
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


def get_archive(playlist_dir: Path):

    archive_path = Path(os.path.join(playlist_dir, "archive.txt"))

    return set(
        line[8:]
        for line in archive_path.read_text(encoding="utf8").splitlines()
        if line.startswith("youtube ")
    )


def get_playlist(config, playlist_url: str):

    yt_dlp_args = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}},  # Force the use of Node.js
        "impersonate": ImpersonateTarget(client="chrome"),  # Disguise as a navigator
    }

    if cookies := config.get("cookies_from_browser"):
        yt_dlp_args["cookiesfrombrowser"] = (cookies,)

    with YoutubeDL(yt_dlp_args) as ydl:
        info = ydl.extract_info(playlist_url)

    video_ids = set()
    for video in info["entries"] or []:
        if video["duration"] is None:
            log.warn('Skipping unavailable video: ID: "%s"', video["id"])
        else:
            video_ids.add(video["id"])

    return video_ids


def append_audio_args(yt_dlp_args, format):

    yt_dlp_args["format"] = "bestaudio/best"
    preferred_codec = format or "best"

    postprocessors = [
        {
            "key": "FFmpegExtractAudio",
            "nopostoverwrites": False,
            "preferredcodec": preferred_codec,
            "preferredquality": "0",
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
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg"}
        )
        postprocessors.append(
            {"key": "EmbedThumbnail", "already_have_thumbnail": False}
        )
        yt_dlp_args["outtmpl"] = {"pl_thumbnail": ""}
        yt_dlp_args["writethumbnail"] = True

    yt_dlp_args["postprocessors"] = postprocessors


def append_video_args(yt_dlp_args, format):

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
        log.warn('Unsupported video format: "%s"', format)


def sync_playlist(config, playlist):

    log.info('Syncing: "%s"', playlist["name"])

    sync_dir = Path(config["sync_dir"]).expanduser()
    playlist_dir = os.path.join(sync_dir, playlist["name"])

    if not os.path.exists(playlist_dir):
        os.mkdir(playlist_dir)

    archive_path = os.path.join(playlist_dir, "archive.txt")
    playlist_name = os.path.basename(playlist_dir)

    yt_dlp_args = {
        "download_archive": archive_path,
        "paths": {"home": playlist_dir},
        "ignoreerrors": "only_download",
        "quiet": True,
        "js_runtimes": {"node": {}},  # Force the use of Node.js
        "impersonate": ImpersonateTarget(client="chrome"),  # Disguise as a navigator
    }

    if cookies := config.get("cookies_from_browser"):
        yt_dlp_args["cookiesfrombrowser"] = (cookies,)

    format = playlist.get("format")
    if playlist.get("convert_to_audio"):
        append_audio_args(yt_dlp_args, format)
    else:
        append_video_args(yt_dlp_args, format)

    if os.path.exists(archive_path):
        archive_ids = get_archive(playlist_dir)
    else:
        log.info('Downloading new playlist at: "%s"', playlist_dir)
        archive_ids = set()
        Path(archive_path).touch()
        log.info('Created: "%s/archive.txt"', playlist_name)

    playlist_ids = get_playlist(config, playlist.get("url"))

    added_ids = playlist_ids - archive_ids
    removed_ids = archive_ids - playlist_ids

    if len(added_ids) == 0 and len(removed_ids) == 0:
        log.info('"%s" is up to date.\n', playlist_name)
        return

    # Download new videos
    if added_ids:
        total = len(added_ids)
        log.info("%d new video(s) to download.", total)

    with YoutubeDL(yt_dlp_args) as ydl:
        for i, id in enumerate(added_ids, start=1):
            log.info('Downloading (%d/%d): ID: "%s"', i, total, id)
            ydl.download(id)

    # Remove videos
    if removed_ids:
        for id in removed_ids:
            remove_item(playlist_dir, id)

        remove_from_archive(playlist_dir, removed_ids)

    log.info('Updated: "%s/archive.txt"', playlist_name)
    log.info('Synced: "%s"\n', playlist_name)


def sync_all(config):

    for playlist in config.get("playlists") or []:
        sync_playlist(config, playlist)

    log.info("Finished Syncing")

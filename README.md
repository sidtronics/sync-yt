# sync-yt
**sync-yt** is a command-line tool that synchronizes YouTube playlists to local directories on your system.
It uses yt-dlp for downloading videos and a JSON based configuration file to define playlists and other options.

## Features
+ Declarative config.json to specify playlists and other configurable options.
+ Option to save playlists in audio-only format, useful for music playlists.
+ Can sync private YouTube playlists by specifying the logged-in browser.
+ Automatically skips repeated video entries.
+ Detects videos which become unavailable.

## Requirements
+ Python 3.10+
+ yt-dlp
+ FFmpeg (Highly recommended)

## Installation
+ From PyPI 
```
$ pip install --user sync-yt
```

OR

+ Build yourself
```
$ git clone https://github.com/sidtronics/sync-yt.git
$ cd sync-yt
$ pip install --user .
```

## Configuration

Configuration file is first searched at `~/.config/sync-yt/config.json` on POSIX compliant systems or at\
`C:\Users\<User>\AppData\Local\sync-yt\config.json` on Windows.

## config.json

### `sync_dir`
- **Type**: `string`
- **Description**: Specifies the local directory where YouTube playlist folders will be synced. This path can be relative to the user's home directory (using `~`) or an absolute path.
- **Examples**: `"~/Music" , "D:\YouTube"`

### `cookies_from_browser`
- **Type**: `string`
- **Description**: Specifies the browser from which cookies should be extracted. This is required for downloading private playlists that are accessible only when signed into a Google account. Supported browsers include `firefox`, `chrome`, `edge`, etc. You can choose to leave this option blank if you're not downloading private playlists.
- **Examples**: `"firefox", "chrome", "brave", "edge", "vivaldi"`

### `playlists`
- **Type**: `array`
- **Description**: An array of playlist objects, where each object represents a YouTube playlist to be synced. Each object in the array has the following properties:

    - **`name`**
      - **Type**: `string`
      - **Description**: A descriptive name to refer the playlist. This is the name of folder created in `sync_dir` where corresponding playlist is synced.

    - **`url`**
      - **Type**: `string`
      - **Description**: The URL of the YouTube playlist.
      - **Example**: `"https://www.youtube.com/playlist?list=PLSdoVPM5WnndSQEXRz704yQkKwx76GvPV"`

    - **`convert_to_audio`**
      - **Type**: `boolean`
      - **Description**: Indicates whether the videos in the playlist should be converted to audio files. If `true`, the videos will be converted to audio.

### Example Configuration

Below is a sample `config.json` file demonstrating the use of the configuration options:

```json
{
    "sync_dir": "~/Music",
    "cookies_from_browser": "firefox",
    "playlists": [
        {
            "name": "Daft Punk - Discovery",
            "url": "https://www.youtube.com/playlist?list=PLSdoVPM5WnndSQEXRz704yQkKwx76GvPV",
            "convert_to_audio": true
        },
        {
            "name": "Minuscule Compilation",
            "url": "https://www.youtube.com/playlist?list=PL7eLsxQrsg-4DNH682TNzgSlCXEeJ3IsX",
            "convert_to_audio": false
        }
    ]
}
```

## Usage
```
$ sync-yt
```


## Notes

+ Manual intervention is needed when a video becomes unavailable. Remove it from upstream youtube playlist to get rid of error/warning.
Upon removal from upstream playlist it will be removed locally as well on next sync. So backup before syncing if needed.
 
+ Two different playlist can share same `name` attribute to sync both playlists in a single folder.

+ You can skip installation of FFmpeg but it is highly recommended especially if you are using `convert_to_audio` option.

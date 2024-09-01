# sync-yt
**sync-yt** is a simple python tool designed to sync YouTube playlists into a designated local folders.
It offers the flexibility to convert videos into audio files, making it ideal for downloading youtube music playlists.
The configuration, including the playlist URLs, sync directory, and conversion options, is managed through a JSON config file.
A key feature of sync-yt is its ability to download private playlists by specifying a browser that is signed into a Google account associated with those playlists,
making it a comprehensive tool for managing YouTube content locally.

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fsidtronics%2Fsync-yt&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

## Download

Clone the repo:
```
$ git clone https://github.com/sidtronics/sync-yt.git
```

or download [zip](https://github.com/sidtronics/sync-yt/archive/refs/heads/main.zip).

## Installation

### Windows:
Install dependencies:
```
$ pip install -r requirements.txt
```

Install ffmpeg:
Follow [this guide](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) to properly install ffmpeg.

### Linux:

You can just install yt-dlp from your distro specific package manager.\
Eg. Arch Linux:
```
# pacman -S yt-dlp
```

**Note:** ffmpeg will be automatically installed as dependency of yt-dlp.

Copy to PATH:
```
$ chmod +x sync_yt.py
# cp sync_yt.py /usr/local/bin/sync-yt
```

## Configuration

Configuration file is first searched at `~/.config/sync-yt/config.json` on POSIX compliant systems or at\
`C:\Users\<User>\AppData\Local\sync-yt\config.json` on Windows. If config file is not found, config file in program directory is used.

On linux copy the sample config file provided to XDG_CONFIG_HOME:
```
$ cp config.json ~/.config/sync-yt/config.json
```


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

### Windows:
In program directory:
```
$ python sync_yt.py
```

### Linux:
```
$ sync-yt
```

## Notes

+ Manual intervention is needed when a video becomes unavailable. Remove it from upstream playlist to get rid of error/warning.
You might want to backup the locally synced video/audio first as it will be deleted upon removal from upstream playlist.

+ Unavailable videos are not deleted locally unless they are removed from upstream playlist.
This can be useful to find replacement video and switch it with unavailable one on upstream playlist.

+ Two different playlist can share same `name` attribute to sync both playlists in single folder.

+ You can skip installation of ffmpeg but it is highly recommended especially if you are using `convert_to_audio` option.

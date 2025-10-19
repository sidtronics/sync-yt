# sync-yt
**sync-yt** is a command-line tool that synchronizes YouTube playlists to local directories on your system.
It uses yt-dlp for downloading videos and a JSON based configuration file to define playlists and other options.

## Features
+ Declarative config.json to specify playlists and other configurable options.
+ Option to save playlists in audio-only format, useful for music playlists.
+ Can sync private YouTube playlists by specifying the logged-in browser.
+ Automatically skips repeated video entries.
+ Detects videos which become unavailable.
+ Add metadata and thumbnail to audio files

## Requirements
+ Python 3.10+
+ yt-dlp
+ FFmpeg (Optional but highly recommended)

## Installation

+ ### Windows
  + #### Install FFmpeg
    Follow this [guide](https://www.geeksforgeeks.org/installation-guide/how-to-install-ffmpeg-on-windows/) to properly install FFmpeg on Windows.
  + #### Install `sync-yt`
    ```
    $ pip install sync-yt
    ```

+ ### Arch Linux
  `sync-yt` is available on [AUR](https://aur.archlinux.org/packages/sync-yt). Use your favourite AUR helper.
  ```
  $ yay -S sync-yt
  ```

+ ### Other Linux Distributions / macOS
  Since `sync-yt` requires the latest version of `yt-dlp`, which may not be available in your OS’s official repositories,
  using `pipx` is recommended.
  + #### Install `pipx`
    ##### Debain and derivatives (Ubuntu, Mint, Zorin etc..)
    ```
    $ sudo apt install pipx
    ``` 
    ##### macOS
    ```
    $ brew install pipx
    ```
  + #### Install `sync-yt`
    ```
    $ pipx ensurepath
    $ pipx install sync-yt
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
      - **Description**: Indicates whether the videos in the playlist should be converted to audio files. Set it to `true` if you want an audio file. If the entry is omitted, it will be set to `false` by default.

    - **`format`**
	  - **Type**: `string`
      - **Description**: Indicate the audio or video codec you want. If the entry is omitted, it will be set to `best` by default.
          - Supported video formats: `avi, flv, mkv, mov, mp4, webm`
          - Supported audio formats (requires `convert_to_audio` set to `true`): `aac, alac, flac, m4a, mp3, opus, vorbis, wav`
      - **Example**: `"mp3"` or `"mkv"`


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
            "format": "mp4"
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

+ metadata and thumbnail will be add to audio files only if the codec is compatible (like .mp3 or .flac)

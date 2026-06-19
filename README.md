# YouTube Playlist Sync

![Release](https://img.shields.io/github/v/release/darkzoul5/YoutubePlaylistSync?style=flat-square&label=Release)
![Build-Release](https://img.shields.io/github/actions/workflow/status/darkzoul5/YoutubePlaylistSync/build-release.yml?style=flat-square&label=Build-Release)
![Unit Tests](https://img.shields.io/github/actions/workflow/status/darkzoul5/YoutubePlaylistSync/unit-tests.yml?style=flat-square&label=unit-tests)

A cross-platform tool for downloading and keeping a local copy of YouTube playlists in sync as MP3 or MP4 files, using [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/).

It supports audio, video, or both download modes, keeps files numbered to match the playlist order, handles playlist cleanup, and exposes configurable parallel download options.
Local-first YouTube playlist synchronization client.

## What's Included

- GUI playlist manager and sync runner built with PySide6 Essentials
- Scanner (yt-dlp extract-only), diff engine, filesystem scan
- Safe reordering via two-pass rename and recycle deletions
- Async download queue with retry support (yt-dlp Python API)
- SQLite metadata for `last_sync` and download state

## Requirements

- If you download a `-ffmpeg` release: no extra dependencies.
- If you download a non-ffmpeg release: install `ffmpeg` and ensure it is on PATH (needed for `audio` and `both` modes).

## Download

Download the latest release from this repo's Releases page and pick one:

- `ytpl-sync-windows-{version}-ffmpeg.zip` / `ytpl-sync-linux-{version}-ffmpeg.tar.gz` (ffmpeg bundled)
- `ytpl-sync-windows-{version}.zip` / `ytpl-sync-linux-{version}.tar.gz` (no ffmpeg bundled)

## Configure

The application uses a JSON config file that can be edited from the UI or manually.

```json
{
  "ffmpeg_path": "./bin/ffmpeg.exe",
  "max_parallel_downloads": 2,
  "retry_max_retries": 2,
  "retry_delay_seconds": 1.5,
  "delay_between_downloads_seconds": 0.0,
  "ui": {
    "tray": {
      "close_to_tray": false,
      "minimize_to_tray": false,
      "start_minimized_to_tray": false
    }
  },
  "playlists": [
    {
      "url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
      "download_mode": "video",
      "max_download_quality": "1080p",
      "save_path": "./downloads",
      "name": "my favorite playlist"
    }
  ]
}
```

`max_download_quality`:

- Limits yt-dlp download quality (e.g. `"2160p"`, `"1440p"`, `"1080p"`, `"720p"`, `"360p"`). This only affects the downloaded video format selection.
- Use `"best"` for no height cap (highest available).
- If the requested max quality isn't available for a video, the best available quality is chosen.

`download_mode`:

- `video`: download playlist videos as `.mp4` (no ffmpeg required)
- `audio`: download the video, extract `.mp3`, and delete the video file
- `both`: download the video, extract `.mp3`, and keep both files

Queue / retry:

- `max_parallel_downloads`: number of concurrent download workers.
- `retry_max_retries`: how many times a failed download job is retried.
- `retry_delay_seconds`: base delay before retry; increases with backoff.
- `delay_between_downloads_seconds`: optional delay between download jobs.

## Run

- GUI: run `ytpl-sync-entry.py` or the packaged desktop exe from releases.

## Tray

- The app supports minimizing to tray on close if the OS provides a system tray; use the tray icon menu to quit.
- Tray behavior settings (Settings page):
  - `close_to_tray`: close hides to tray (keeps running).
  - `minimize_to_tray`: minimize hides to tray.
  - `start_minimized_to_tray`: start hidden in tray.

## Data & Layout

- Database: `db/app.db`
- Outputs: `<save_path>/audio` and/or `<save_path>/video`
- Recycle bin: `<save_path>/.recycle/{audio,video}`

## Roadmap (short)

- Scheduler (periodic sync), richer retries/logging
- Enhanced config validation
- UX polish (settings, progress, error messages)

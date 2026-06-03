# YouTube Playlist Sync — Project Conversion Plan


---

# Project Direction

Convert the project from:

```text
Single-purpose YouTube playlist downloader
```

into:

```text
Persistent YouTube playlist synchronization client
```

The application becomes state-driven.

---

# Core Product Goals

## Main Features

- Sync playlists locally
- Download missing items
- Remove deleted playlist items
- Keep exact playlist ordering
- Support audio/video modes
- Multiple playlists
- Background auto-sync
- GUI configuration
- Queue management
- Logs/history

---

# Explicit Non-Goals (Current Scope)

Not planned right now:

- Built-in media playback
- Advanced naming templates
- Drag-and-drop manual ordering
- Private playlist sync
- Channel subscriptions
- Metadata editing

Design the architecture so these can be added later.

---

# Recommended Stack

## Core Language

- Python 3.12+

Reason:

- Native yt-dlp ecosystem
- Easier async/background work
- Better packaging than many expect
- Simpler iteration speed

---

# GUI

## Recommended

- PySide6

Why:

- Modern Qt ecosystem
- Better long-term support
- Cleaner than Tkinter
- Easier dynamic playlist UI
- Good threading support
- Better styling

Avoid:

- Tkinter for this scale
- Electron/Tauri unless you want a web stack

---

# Downloader Backend

## Recommended

- yt-dlp Python API

Install:

```bash
pip install yt-dlp
```

Do NOT:

- scrape YouTube manually
- parse HTML yourself
- depend on external unofficial APIs

Use yt-dlp for:

- metadata extraction
- playlist scanning
- downloading
- postprocessing

Use your own app for:

- sync logic
- ordering
- deletion
- scheduling
- state tracking

---

# Media Processing

## Recommended

- ffmpeg

Needed for:

- audio extraction
- remuxing
- conversions
- thumbnail embedding later

Recommended approach:

- auto-detect ffmpeg
- optionally bundle with packaged app

---

# Database

## Recommended

- SQLite

Reason:

- Zero setup
- Local-first architecture
- Perfect for sync metadata
- Easy migrations
- Reliable

SQLite is extremely important for this project.

Do NOT rely only on:

- filenames
- folders
- JSON

---

# Background Scheduling

## Recommended

- APScheduler

Use for:

- interval syncs
- delayed jobs
- retry jobs
- startup sync

---

# Async/Concurrency

## Recommended

- asyncio

Use for:

- concurrent playlist syncs
- GUI-safe task execution
- download queue
- cancellation
- progress updates

---

# Logging

## Recommended

- loguru

or:

- standard logging module

Need:

- rotating logs
- GUI log panel
- error history
- debug support

---

# Packaging

## Recommended

### During development

```text
venv + pip
```

### Release builds

Choose one:

| Tool        | Notes                           |
| ----------- | ------------------------------- |
| Nuitka      | Best performance and protection |
| PyInstaller | Easier and common               |

Nuitka is probably best long-term.

---

# Major Architectural Changes

---

# 1. Move to State-Based Sync Architecture

Current downloader logic is likely:

```text
Playlist URL
↓
Download everything
```

Replace with:

```text
Remote Playlist State
↓
Stored Local State
↓
Filesystem State
↓
Diff Engine
↓
Sync Actions
```

This is the single most important change.

---

# 2. Introduce Playlist Metadata Database

Create persistent tracking.

Suggested tables:

## playlists

```sql
CREATE TABLE playlists (
    id TEXT PRIMARY KEY,
    name TEXT,
    url TEXT,
    path TEXT,
    mode TEXT,
    auto_sync INTEGER,
    sync_interval_minutes INTEGER,
    last_sync TEXT
);
```

## playlist\_items

```sql
CREATE TABLE playlist_items (
    playlist_id TEXT,
    video_id TEXT,
    title TEXT,
    playlist_index INTEGER,
    local_filename TEXT,
    downloaded INTEGER,
    last_seen TEXT,
    PRIMARY KEY (playlist_id, video_id)
);
```

---

# 3. Implement Playlist Scanner Layer

Create dedicated metadata extraction.

Suggested structure:

```text
core/
 ├── scanner/
 │    └── playlist_scanner.py
```

Responsibilities:

- fetch playlist entries
- extract video IDs
- detect unavailable videos
- return normalized playlist state

Use:

```python
extract_info(download=False)
```

This allows playlist scanning without downloading.

---

# 4. Create Diff Engine

The app should compare:

```text
Remote playlist
vs
Database state
vs
Filesystem state
```

Output actions:

```text
DOWNLOAD
DELETE
RENAME
REORDER
SKIP
REPAIR
```

Suggested file:

```text
core/sync/diff_engine.py
```

This becomes the heart of the application.

---

# 5. Add Download Queue System

Multi-playlist sync requires a queue.

Suggested states:

```text
Queued
Downloading
Converting
Completed
Failed
Skipped
Cancelled
```

Suggested structure:

```text
core/download/
 ├── queue_manager.py
 ├── downloader.py
 └── workers.py
```

---

# 6. Implement Stable File Naming

Recommended naming:

```text
0001 - Title.ext
```

Benefits:

- native filesystem sorting
- easy reorder support
- easy repairs
- user friendly

Use:

```python
%(playlist_index)04d - %(title)s.%(ext)s
```

through yt-dlp.

---

# 7. Implement Safe Reordering

Playlist ordering changes frequently.

Never rename directly.

Use:

```text
Temporary rename pass
↓
Final rename pass
```

Example:

```text
0001.mp3 → temp_a
0002.mp3 → temp_b
↓
temp_a → 0002.mp3
```

Avoid collisions.

---

# 8. Implement Deletion Strategy

Recommended:

Instead of immediate delete:

```text
playlist/.recycle/
```

Move removed files there.

Benefits:

- safer
- recoverable
- easier debugging

Optional:

- auto-clean after X days

---

# 9. Redesign GUI Around Playlists

Current downloader GUIs are usually task-oriented.

You should move to:

```text
Playlist-oriented UI
```

Recommended sections:

```text
Sidebar
 ├── Playlists
 ├── Queue
 ├── History
 ├── Logs
 └── Settings
```

---

# 10. Support Infinite Playlist Entries

Use dynamic UI generation.

Example:

```python
class PlaylistConfig:
    url: str
    path: str
    mode: str
    auto_sync: bool
```

GUI should render from:

```python
list[PlaylistConfig]
```

Do NOT hardcode playlist pages.

---

# 11. Add Background Sync

Start simple.

## Phase 1

- Timer-based sync
- Tray icon
- Run minimized

## Phase 2

- Background daemon/service
- Headless mode
- Autostart support

---

# 12. Add Progress/Event System

Needed for GUI responsiveness.

Recommended:

```text
event_bus.py
```

Events:

```text
DownloadStarted
DownloadProgress
SyncStarted
SyncFinished
FileDeleted
PlaylistUpdated
```

This decouples GUI from backend.

---

# 13. Introduce Config Management

Recommended:

```text
config.json
```

Only for:

- app settings
- UI preferences
- non-relational settings

Do NOT store sync state in JSON.

---

# Suggested Folder Structure

```text
app/
 ├── core/
 │    ├── scanner/
 │    ├── sync/
 │    ├── download/
 │    ├── database/
 │    ├── scheduler/
 │    └── events/
 │
 ├── gui/
 │    ├── pages/
 │    ├── widgets/
 │    ├── dialogs/
 │    └── models/
 │
 ├── config/
 ├── logs/
 ├── data/
 └── main.py
```

---

# Suggested Sync Flow

```text
Load playlists
↓
Scheduler triggers sync
↓
Scanner fetches remote playlist
↓
Database state loaded
↓
Filesystem scanned
↓
Diff engine computes actions
↓
Queue downloads
↓
Reorder files
↓
Move removed files
↓
Update database
↓
Emit GUI events
```

---

# Recommended MVP Conversion Order

## Phase 1 — Backend Foundation

Implement:

- SQLite
- playlist scanner
- diff engine
- download wrapper
- basic sync logic

No GUI redesign yet.

---

# Phase 2 — Stable Syncing

Implement:

- deletion handling
- reorder handling
- queue system
- retry system
- logs

---

# Phase 3 — GUI Rewrite

Implement:

- playlist manager UI
- queue page
- logs page
- settings page
- dynamic playlists

---

# Phase 4 — Automation

Implement:

- background sync
- tray mode
- startup sync
- periodic sync

---

# Important Recommendations

## Recommendation 1

Treat:

```text
video_id
```

as the canonical identity.

Never titles.

---

# Recommendation 2

Do NOT rely on yt-dlp archive files alone.

Your own DB should be the source of truth.

---

# Recommendation 3

Keep download logic isolated.

yt-dlp should be replaceable internally.

---

# Recommendation 4

Do not overcomplicate the GUI early.

Focus on sync correctness first.

Sync reliability matters more than appearance.

---

# Recommendation 5

Design everything around interruption recovery.

The app should survive:

- crashes
- partial downloads
- force closes
- network failures
- playlist changes mid-sync

---

# Recommendation 6

Keep the application local-first.

No account system. No cloud backend. No telemetry.

That becomes a strong project identity.

---

# Final Recommended Identity

Instead of:

```text
YouTube Downloader GUI
```

Position the project as:

```text
Local-first YouTube playlist synchronization client.
```

That identity is:

- clearer
- more unique
- technically stronger
- easier to expand later

# GUI Plan

## Python-first Desktop Architecture

- **Primary GUI framework**: `PySide6` (Qt for Python).

## Core Features to Implement

1. **Dashboard Overview**: List all tracked playlists, their status (Last Sync), and total size.
2. **Interactive Configuration**: Wizard-style setup for new playlists (URL detection, folder picker).
3. **Queue Manager**: Visual progress bars for active downloads, showing speed, ETA, and current video title.
4. **Log Viewer**: Real-time streaming of yt-dlp logs for troubleshooting.
5. **Settings Panel**: Global settings for binary paths (ffmpeg), max parallel jobs, and Docker detection toggle.

## Phase 1 Roadmap: "The Bridge"

- [ ] **PySide6 Skeleton**: Basic window with `QWebEngine` (if hybrid) or native `QWidget` dashboard.
- [ ] **Packaging**: `pyinstaller` configuration to bundle both backend and frontend into a single `.exe`.

## Packaging & Distribution (brief)

- Bundle the backend and GUI into one distributable.
- Windows: use `pyinstaller` or `briefcase` to create an executable/installer. Consider creating an MSI or Inno Setup installer for a polished UX.
- Linux: provide AppImage, Snap, or distribution-specific packages (deb/rpm) — AppImage is a good starting point for single-file distribution.
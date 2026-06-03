from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class AboutPage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("About")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "ytpl-sync is a desktop app for keeping local copies of YouTube playlists in sync."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        note = QtWidgets.QLabel(
            "This project started as a student project and is still evolving."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        info_box = QtWidgets.QGroupBox("Project")
        info_layout = QtWidgets.QFormLayout(info_box)

        author = QtWidgets.QLabel("Dark_Zoul")
        info_layout.addRow("Author", author)

        repo = QtWidgets.QLabel(
            '<a href="https://github.com/darkzoul5/YoutubePlaylistSync">'
            "https://github.com/darkzoul5/YoutubePlaylistSync</a>"
        )
        repo.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
        )
        repo.setOpenExternalLinks(True)
        repo.setWordWrap(True)
        info_layout.addRow("Repository", repo)

        issue = QtWidgets.QLabel(
            '<a href="https://github.com/darkzoul5/YoutubePlaylistSync/issues">'
            "https://github.com/darkzoul5/YoutubePlaylistSync/issues</a>"
        )
        issue.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
        )
        issue.setOpenExternalLinks(True)
        issue.setWordWrap(True)
        info_layout.addRow("Report issue", issue)

        layout.addWidget(info_box)

        suggestions_box = QtWidgets.QGroupBox("Suggestions")
        suggestions_layout = QtWidgets.QVBoxLayout(suggestions_box)

        suggestions = [
            "Keep yt-dlp updated regularly so site extraction stays reliable.",
            "Open an issue with a playlist URL and log snippet when a sync fails.",
            "Use the release builds when you want a ready-to-run binary package.",
        ]
        for text in suggestions:
            label = QtWidgets.QLabel(f"• {text}")
            label.setWordWrap(True)
            suggestions_layout.addWidget(label)

        suggestions_layout.addStretch(1)
        layout.addWidget(suggestions_box)
        layout.addStretch(1)

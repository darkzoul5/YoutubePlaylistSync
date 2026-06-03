from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class AboutPage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("aboutPage")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("About")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "ytpl-sync is a desktop app for keeping local copies of YouTube playlists in sync."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("muted", True)
        layout.addWidget(subtitle)

        note = QtWidgets.QLabel(
            "This project is a student project."
        )
        note.setWordWrap(True)
        note.setProperty("muted", True)
        layout.addWidget(note)

        info_box = QtWidgets.QGroupBox("Project")
        info_box.setObjectName("aboutCard")
        info_layout = QtWidgets.QFormLayout(info_box)
        info_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        info_layout.setFormAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        info_layout.setHorizontalSpacing(14)
        info_layout.setVerticalSpacing(10)

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
        repo.setProperty("link", True)
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
        issue.setProperty("link", True)
        info_layout.addRow("Report issue", issue)

        layout.addWidget(info_box)

        suggestions_box = QtWidgets.QGroupBox("Suggestions")
        suggestions_box.setObjectName("aboutCard")
        suggestions_layout = QtWidgets.QVBoxLayout(suggestions_box)
        suggestions_layout.setSpacing(8)

        suggestions = [
            "Keep the app updated regularly so that YouTube extraction stays reliable."
        ]
        for text in suggestions:
            label = QtWidgets.QLabel(f"• {text}")
            label.setWordWrap(True)
            label.setProperty("muted", True)
            suggestions_layout.addWidget(label)

        suggestions_layout.addStretch(1)
        layout.addWidget(suggestions_box)
        layout.addStretch(1)

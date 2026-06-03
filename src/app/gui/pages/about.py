from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class AboutPage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("aboutPage")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QtWidgets.QLabel("About")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._hero_card())
        layout.addWidget(self._project_card())
        layout.addWidget(self._suggestions_card())
        layout.addStretch(1)

    def _card(self) -> tuple[QtWidgets.QFrame, QtWidgets.QVBoxLayout]:
        card = QtWidgets.QFrame()
        card.setObjectName("aboutCard")

        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)
        return card, card_layout

    def _card_title(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        label.setObjectName("cardTitle")
        return label

    def _muted_label(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        label.setWordWrap(True)
        label.setProperty("muted", True)
        return label

    def _link_label(self, text: str, url: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(f'<a href="{url}">{text}</a>')
        label.setWordWrap(True)
        label.setProperty("link", True)
        label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
        )
        label.setOpenExternalLinks(True)
        return label

    def _hero_card(self) -> QtWidgets.QFrame:
        card, layout = self._card()
        layout.addWidget(self._card_title("About this project"))
        layout.addWidget(
            self._muted_label(
                "ytpl-sync is a desktop app for keeping local copies of YouTube playlists in sync."
            )
        )
        layout.addWidget(
            self._muted_label(
                "This is a student project."
            )
        )
        return card

    def _project_card(self) -> QtWidgets.QFrame:
        card, layout = self._card()
        layout.addWidget(self._card_title("Project"))

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        author = self._muted_label("Dark_Zoul")
        form.addRow("Author", author)
        form.addRow(
            "Repository",
            self._link_label(
                "https://github.com/darkzoul5/YoutubePlaylistSync",
                "https://github.com/darkzoul5/YoutubePlaylistSync",
            ),
        )
        form.addRow(
            "Report issue",
            self._link_label(
                "https://github.com/darkzoul5/YoutubePlaylistSync/issues",
                "https://github.com/darkzoul5/YoutubePlaylistSync/issues",
            ),
        )

        layout.addLayout(form)
        return card

    def _suggestions_card(self) -> QtWidgets.QFrame:
        card, layout = self._card()
        layout.addWidget(self._card_title("Suggestions"))

        suggestions = [
            "Keep the app updated regularly so that YouTube extraction stays reliable."
        ]
        for text in suggestions:
            layout.addWidget(self._muted_label(f"• {text}"))

        layout.addStretch(1)
        return card

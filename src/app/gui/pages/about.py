from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from ...core.utils.version import get_app_version


class AboutPage(QtWidgets.QWidget):
    REPO_URL = "https://github.com/darkzoul5/YoutubePlaylistSync"
    ISSUES_URL = f"{REPO_URL}/issues"

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("aboutPage")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QtWidgets.QLabel("About")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        for card in (
            self._hero_card(),
            self._project_card(),
            self._suggestions_card(),
        ):
            layout.addWidget(card)
        layout.addStretch(1)

    def _card(self, title: str) -> tuple[QtWidgets.QFrame, QtWidgets.QVBoxLayout]:
        card = QtWidgets.QFrame()
        card.setObjectName("aboutCard")

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(self._card_title(title))
        return card, layout

    def _card_title(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        label.setObjectName("cardTitle")
        return label

    def _muted_label(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        label.setWordWrap(True)
        label.setProperty("muted", True)
        return label

    def _link_button(self, text: str, url: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(text)
        button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(url)))
        return button

    def _action_row(self, text: str, url: str) -> QtWidgets.QWidget:
        row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self._link_button(text, url))
        layout.addStretch(1)
        return row

    def _hero_card(self) -> QtWidgets.QFrame:
        card, layout = self._card("About this project")
        layout.insertWidget(
            1,
            self._muted_label(
                "ytpl-sync is a desktop app for keeping local copies of YouTube playlists in sync."
            ),
        )
        layout.insertWidget(2, self._muted_label("This is a student project."))
        return card

    def _project_card(self) -> QtWidgets.QFrame:
        card, layout = self._card("Project")

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        version_text = get_app_version()
        version = f"v{version_text}" if version_text != "dev" else version_text
        rows = [
            ("Author", self._muted_label("Dark_Zoul")),
            ("Version", self._muted_label(version)),
            ("Repository", self._action_row("Open", self.REPO_URL)),
            ("Issues", self._action_row("Open", self.ISSUES_URL)),
        ]
        for label, widget in rows:
            form.addRow(label, widget)

        layout.addLayout(form)
        return card

    def _suggestions_card(self) -> QtWidgets.QFrame:
        card, layout = self._card("Suggestions")
        layout.addWidget(
            self._muted_label(
                "• Keep the app updated regularly so that YouTube extraction stays reliable."
            )
        )
        layout.addStretch(1)
        return card

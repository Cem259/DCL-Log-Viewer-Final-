from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QVBoxLayout, QWidget


class SplashIntro(QWidget):
    """Widget that plays the intro video before the main window is shown."""

    finished = Signal()

    _INTRO_FILENAME = "ckn_airlogic_final_intro_v4.mp4"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent, flags=Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal)

        self._video_widget = QVideoWidget(self)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.setVideoOutput(self._video_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._video_widget)

        self._video_path = self._resolve_video_path()
        self._has_finished = False
        self._connect_signals()

        if self._video_path.exists():
            url = QUrl.fromLocalFile(str(self._video_path))
            self._player.setSource(url)

    @property
    def is_available(self) -> bool:
        """Return ``True`` when the intro video is available for playback."""

        return self._video_path.exists()

    def start(self) -> None:
        """Start playback of the intro video."""

        if self.is_available:
            self.showFullScreen()
            self._player.play()
        else:
            self._finish()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        """Allow the user to skip the intro with a mouse click."""

        event.accept()
        self._finish()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        """Allow the user to skip the intro with a key press."""

        event.accept()
        self._finish()

    def _connect_signals(self) -> None:
        self._player.mediaStatusChanged.connect(self._handle_media_status)
        self._player.errorOccurred.connect(self._handle_error)

    @Slot()
    def _finish(self) -> None:
        if self._player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self._player.stop()
        if not self._has_finished:
            self._has_finished = True
            self.close()
            self.finished.emit()

    @Slot(QMediaPlayer.MediaStatus)
    def _handle_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._finish()

    @Slot(QMediaPlayer.Error, str)
    def _handle_error(self, error: QMediaPlayer.Error, message: str) -> None:
        if error != QMediaPlayer.Error.NoError:
            # Skip the intro if the video cannot be played.
            self._finish()

    def _resolve_video_path(self) -> Path:
        root = Path(__file__).resolve().parents[2]
        return root / "assets" / self._INTRO_FILENAME

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPreviewService(QObject):
    playback_state_changed = Signal(str)
    source_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.75)
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.current_source: Path | None = None
        self.player.playbackStateChanged.connect(self._emit_state)

    def play(self, audio_path: Path) -> None:
        if self.current_source != audio_path:
            self.current_source = audio_path
            self.player.setSource(QUrl.fromLocalFile(str(audio_path)))
            self.source_changed.emit(str(audio_path))
        self.player.play()

    def pause(self) -> None:
        self.player.pause()

    def stop(self) -> None:
        self.player.stop()

    def _emit_state(self) -> None:
        self.playback_state_changed.emit(self.player.playbackState().name)

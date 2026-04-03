from __future__ import annotations

import json
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TrackRecord:
    audio_path: Path
    prompt_path: Path
    metadata_path: Path
    name: str
    created_at: datetime
    duration_seconds: float
    prompt_text: str
    metadata: dict[str, Any]
    display_metadata: dict[str, Any]


class LibraryService:
    def __init__(self, music_dir: Path) -> None:
        self.music_dir = music_dir
        self.music_dir.mkdir(parents=True, exist_ok=True)

    def scan_tracks(self) -> list[TrackRecord]:
        records: list[TrackRecord] = []
        for audio_path in sorted(self.music_dir.glob("*.wav"), key=lambda path: path.stat().st_mtime, reverse=True):
            prompt_path = audio_path.with_suffix(".prompt.txt")
            metadata_path = audio_path.with_suffix(".json")
            prompt_text = prompt_path.read_text(encoding="utf-8").strip() if prompt_path.exists() else ""
            metadata = self._load_json(metadata_path)
            display_metadata = metadata.get("display", {}) if isinstance(metadata.get("display", {}), dict) else {}
            created_at = datetime.fromtimestamp(audio_path.stat().st_mtime)
            duration_seconds = self._read_duration(audio_path)
            records.append(
                TrackRecord(
                    audio_path=audio_path,
                    prompt_path=prompt_path,
                    metadata_path=metadata_path,
                    name=audio_path.stem,
                    created_at=created_at,
                    duration_seconds=duration_seconds,
                    prompt_text=prompt_text,
                    metadata=metadata,
                    display_metadata=display_metadata,
                )
            )
        return records

    def rename_track(self, record: TrackRecord, new_stem: str) -> TrackRecord:
        sanitized = new_stem.strip()
        if not sanitized:
            raise ValueError("Track name cannot be empty.")

        target_audio = record.audio_path.with_name(f"{sanitized}{record.audio_path.suffix}")
        if target_audio.exists() and target_audio != record.audio_path:
            raise FileExistsError(f"Target file already exists: {target_audio.name}")

        record.audio_path.rename(target_audio)

        target_prompt = target_audio.with_suffix(".prompt.txt")
        target_metadata = target_audio.with_suffix(".json")
        if record.prompt_path.exists():
            record.prompt_path.rename(target_prompt)
        if record.metadata_path.exists():
            record.metadata_path.rename(target_metadata)

        updated = self.scan_tracks()
        for candidate in updated:
            if candidate.audio_path == target_audio:
                return candidate
        raise FileNotFoundError(f"Renamed track could not be reloaded: {target_audio}")

    def delete_track(self, record: TrackRecord) -> None:
        for path in (record.audio_path, record.prompt_path, record.metadata_path):
            if path.exists():
                path.unlink()

    def open_in_explorer(self, record: TrackRecord) -> None:
        import os

        os.startfile(str(record.audio_path.parent))

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _read_duration(audio_path: Path) -> float:
        try:
            with wave.open(str(audio_path), "rb") as wav_file:
                frame_rate = wav_file.getframerate()
                if frame_rate <= 0:
                    return 0.0
                return wav_file.getnframes() / float(frame_rate)
        except (OSError, EOFError, wave.Error):
            return 0.0

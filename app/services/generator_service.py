from __future__ import annotations

import json
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from app.core.musicgen_engine import (
    DEFAULT_MODEL,
    GenerationResult,
    GenerationSettings,
    default_cache_dir,
    generate_music,
    is_model_cached,
)


@dataclass
class GenerationJob:
    job_id: str
    title: str
    prompt: str
    out_path: Path
    seconds: int
    model: str
    seed: int | None
    metadata: dict[str, Any]
    status: str = "排隊中"
    created_at: float = field(default_factory=time.time)


class GenerationWorker(QObject):
    stage_message = Signal(str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, settings: GenerationSettings) -> None:
        super().__init__()
        self.settings = settings

    @Slot()
    def run(self) -> None:
        try:
            result = generate_music(self.settings, status_callback=self.stage_message.emit)
            self.completed.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class GeneratorService(QObject):
    queue_changed = Signal(object)
    job_progress = Signal(object)
    job_completed = Signal(object)
    job_failed = Signal(object, str)
    log_message = Signal(str)
    active_job_changed = Signal(object)

    def __init__(self, repo_root: Path) -> None:
        super().__init__()
        self.repo_root = repo_root
        self.cache_dir = default_cache_dir()
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(1000)
        self.progress_timer.timeout.connect(self._tick_progress)
        self._queue: deque[GenerationJob] = deque()
        self._active_job: GenerationJob | None = None
        self._started_at: float = 0.0
        self._active_thread: QThread | None = None
        self._active_worker: GenerationWorker | None = None

    def environment_issue(self) -> str | None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return f"無法建立模型快取資料夾：{exc}"
        return None

    def model_cache_path(self) -> Path:
        return self.cache_dir

    def is_model_ready(self, model_name: str = DEFAULT_MODEL) -> bool:
        return is_model_cached(model_name, self.cache_dir)

    def enqueue_job(
        self,
        *,
        title: str,
        prompt: str,
        out_path: Path,
        seconds: int,
        model: str,
        seed: int | None,
        metadata: dict[str, Any],
    ) -> None:
        job = GenerationJob(
            job_id=str(uuid.uuid4()),
            title=title,
            prompt=prompt,
            out_path=out_path,
            seconds=seconds,
            model=model,
            seed=seed,
            metadata=metadata,
        )
        self._queue.append(job)
        self.queue_changed.emit(list(self._queue))
        self.log_message.emit(f"已加入佇列：{title}")
        self._start_next_if_idle()

    def clear_pending_queue(self) -> None:
        self._queue.clear()
        self.queue_changed.emit(list(self._queue))
        self.log_message.emit("已清空等待中的任務。")

    def current_job(self) -> GenerationJob | None:
        return self._active_job

    def _start_next_if_idle(self) -> None:
        if self._active_job is not None or not self._queue:
            return

        issue = self.environment_issue()
        if issue is not None:
            placeholder = GenerationJob(
                job_id="environment",
                title="環境檢查失敗",
                prompt="",
                out_path=self.repo_root / "music" / "invalid.wav",
                seconds=0,
                model="",
                seed=None,
                metadata={},
                status="失敗",
            )
            self.job_failed.emit(placeholder, issue)
            return

        self._active_job = self._queue.popleft()
        self._active_job.status = "準備中"
        self.queue_changed.emit(list(self._queue))
        self.active_job_changed.emit(self._active_job)
        self._started_at = time.time()

        settings = GenerationSettings(
            prompt=self._active_job.prompt,
            out_path=self._active_job.out_path,
            model=self._active_job.model,
            seconds=self._active_job.seconds,
            seed=self._active_job.seed,
            cache_dir=self.cache_dir,
        )
        self._active_worker = GenerationWorker(settings)
        self._active_thread = QThread()
        self._active_worker.moveToThread(self._active_thread)
        self._active_thread.started.connect(self._active_worker.run)
        self._active_worker.stage_message.connect(self._forward_stage_message)
        self._active_worker.completed.connect(self._complete_job)
        self._active_worker.failed.connect(self._fail_job)
        self._active_worker.completed.connect(self._cleanup_thread)
        self._active_worker.failed.connect(self._cleanup_thread)
        self._active_thread.start()
        self.progress_timer.start()
        self.job_progress.emit(
            {
                "job": self._active_job,
                "percent": 3,
                "status": "正在準備模型與提示詞。",
            }
        )

    def _tick_progress(self) -> None:
        if self._active_job is None:
            return

        elapsed = max(0, int(time.time() - self._started_at))
        estimate = max(20, int(self._active_job.seconds * 4.5))
        percent = min(95, max(6, int((elapsed / estimate) * 100)))
        self.job_progress.emit(
            {
                "job": self._active_job,
                "percent": percent,
                "status": f"生成中，已經過 {elapsed} 秒，依目前硬體估計約需 {estimate} 秒。",
            }
        )

    def _forward_stage_message(self, message: str) -> None:
        if self._active_job is None:
            return
        self.log_message.emit(message)
        self.job_progress.emit(
            {
                "job": self._active_job,
                "percent": max(8, self._estimate_progress_floor()),
                "status": message,
            }
        )

    def _estimate_progress_floor(self) -> int:
        if self._active_job is None:
            return 0
        elapsed = max(0, int(time.time() - self._started_at))
        estimate = max(20, int(self._active_job.seconds * 4.5))
        return min(90, max(8, int((elapsed / estimate) * 100)))

    def _complete_job(self, result: GenerationResult) -> None:
        if self._active_job is None:
            return

        self.progress_timer.stop()
        self._write_metadata(self._active_job, result)
        self._active_job.status = "完成"
        self.job_progress.emit(
            {
                "job": self._active_job,
                "percent": 100,
                "status": "完成",
            }
        )
        completed_job = self._active_job
        self._active_job = None
        self.active_job_changed.emit(None)
        self.job_completed.emit(completed_job)
        self._start_next_if_idle()

    def _fail_job(self, details: str) -> None:
        if self._active_job is None:
            return

        self.progress_timer.stop()
        failed_job = self._active_job
        failed_job.status = "失敗"
        self._active_job = None
        self.active_job_changed.emit(None)
        self.job_failed.emit(failed_job, details)
        self._start_next_if_idle()

    def _cleanup_thread(self, *_args) -> None:
        if self._active_thread is not None:
            self._active_thread.quit()
            self._active_thread.wait()
            self._active_thread = None
        if self._active_worker is not None:
            self._active_worker.deleteLater()
            self._active_worker = None

    def _write_metadata(self, job: GenerationJob, result: GenerationResult) -> None:
        payload = {
            "job_id": job.job_id,
            "created_at": job.created_at,
            "title": job.title,
            "prompt": job.prompt,
            "seconds": job.seconds,
            "model": job.model,
            "seed": job.seed,
            "cache_dir": str(result.cache_dir),
            "downloaded_now": result.downloaded_now,
            **job.metadata,
        }
        metadata_path = job.out_path.with_suffix(".json")
        metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

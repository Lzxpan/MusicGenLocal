from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.prompting.prompt_builder import (
    COMPLEXITY_OPTIONS,
    DURATION_OPTIONS,
    ENERGY_OPTIONS,
    INSTRUMENT_OPTIONS,
    KEY_OPTIONS,
    MODEL_OPTIONS,
    MOOD_OPTIONS,
    STYLE_OPTIONS,
    TONALITY_OPTIONS,
    TYPE_OPTIONS,
    ChoiceOption,
    PromptFormData,
    build_metadata_sections,
    build_prompt,
    label_for_token,
    suggested_filename,
)
from app.services.audio_preview_service import AudioPreviewService
from app.services.generator_service import GenerationJob, GeneratorService
from app.services.library_service import LibraryService, TrackRecord


class MainWindow(QMainWindow):
    def __init__(self, repo_root: Path) -> None:
        super().__init__()
        self.repo_root = repo_root
        self.music_dir = repo_root / "music"
        self.library_service = LibraryService(self.music_dir)
        self.generator_service = GeneratorService(repo_root)
        self.audio_preview_service = AudioPreviewService()
        self.tracks: list[TrackRecord] = []

        self.setWindowTitle("MusicGenLocal 音樂工作站 V0.91b")
        self.resize(1560, 980)

        self._build_ui()
        self._connect_signals()
        self._sync_environment_banner()
        self._update_prompt_preview()
        self._refresh_library()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)
        self.setCentralWidget(root)

        header_layout = QHBoxLayout()
        title = QLabel("MusicGenLocal 音樂工作站 V0.91b")
        title.setProperty("title", True)
        subtitle = QLabel("用中文選風格、調整提示詞、排入佇列，再直接試聽與整理成品。")
        subtitle.setStyleSheet("color: #51617e;")
        text_layout = QVBoxLayout()
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        header_layout.addLayout(text_layout)
        header_layout.addStretch(1)

        self.environment_banner = QLabel()
        self.environment_banner.setWordWrap(True)
        self.environment_banner.setStyleSheet(
            "background: #eef4ff; color: #23407a; padding: 10px 12px; border-radius: 12px;"
        )
        header_layout.addWidget(self.environment_banner, 0, Qt.AlignRight)
        root_layout.addLayout(header_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_center_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([460, 520, 520])
        root_layout.addWidget(splitter, 1)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("準備完成")

    def _build_left_panel(self) -> QWidget:
        card = self._create_card()
        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        section = QLabel("生成參數")
        section.setProperty("section", True)
        layout.addWidget(section)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        form_host = QWidget()
        form = QVBoxLayout(form_host)
        form.setSpacing(10)

        self.style_combo = self._create_combo(STYLE_OPTIONS, "arcade")
        self.type_combo = self._create_combo(TYPE_OPTIONS, "bgm")
        self.mood_combo = self._create_combo(MOOD_OPTIONS, "bright")
        self.key_combo = self._create_combo(KEY_OPTIONS, "C")
        self.tonality_combo = self._create_combo(TONALITY_OPTIONS, "minor")
        self.complexity_combo = self._create_combo(COMPLEXITY_OPTIONS, "balanced")
        self.energy_combo = self._create_combo(ENERGY_OPTIONS, "medium")
        self.model_combo = self._create_combo(MODEL_OPTIONS, "facebook/musicgen-small")

        self.bpm_spin = QSpinBox()
        self.bpm_spin.setRange(60, 220)
        self.bpm_spin.setValue(125)

        self.duration_combo = QComboBox()
        for seconds in DURATION_OPTIONS:
            self.duration_combo.addItem(f"{seconds} 秒", seconds)
        self.duration_combo.setCurrentIndex(DURATION_OPTIONS.index(8))

        self.loop_checkbox = QCheckBox("偏向無縫循環")
        self.loop_checkbox.setChecked(True)

        self.seed_checkbox = QCheckBox("使用固定 Seed")
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2_147_483_647)
        self.seed_spin.setValue(42)
        self.seed_spin.setEnabled(False)

        self.instrument_list = QListWidget()
        self.instrument_list.setMaximumHeight(165)
        for option in INSTRUMENT_OPTIONS:
            item = QListWidgetItem(option.label)
            item.setData(Qt.UserRole, option.token)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if option.token in {"synth", "bass", "drums"} else Qt.Unchecked)
            self.instrument_list.addItem(item)

        self.prompt_boost_edit = QTextEdit()
        self.prompt_boost_edit.setPlaceholderText("自由補強，例如：乾淨低頻、商業感混音、復古但不刺耳、尾端更自然。")
        self.prompt_boost_edit.setFixedHeight(96)

        self.prompt_preview_edit = QTextEdit()
        self.prompt_preview_edit.setPlaceholderText("這裡顯示實際送進模型的英文提示詞；送出前可手動微調。")
        self.prompt_preview_edit.setFixedHeight(160)

        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("留空會自動命名，例如 20260403-arcade-bgm-125bpm.wav")

        form.addWidget(self._field_row("風格", self.style_combo))
        form.addWidget(self._field_row("類型", self.type_combo))
        form.addWidget(self._field_row("情緒", self.mood_combo))
        form.addWidget(self._field_row("節奏 / BPM", self.bpm_spin))
        form.addWidget(self._field_row("調性主音", self.key_combo))
        form.addWidget(self._field_row("大小調", self.tonality_combo))
        form.addWidget(self._field_row("時長", self.duration_combo))
        form.addWidget(self._field_row("編曲複雜度", self.complexity_combo))
        form.addWidget(self._field_row("能量感", self.energy_combo))
        form.addWidget(self._field_row("模型", self.model_combo))
        form.addWidget(self.loop_checkbox)
        form.addWidget(self._field_row("固定 Seed", self.seed_spin, leading=self.seed_checkbox))
        form.addWidget(self._section_text("樂器選擇"))
        form.addWidget(self.instrument_list)
        form.addWidget(self._section_text("補強描述"))
        form.addWidget(self.prompt_boost_edit)
        form.addWidget(self._section_text("最終生成提示詞"))
        form.addWidget(self.prompt_preview_edit)
        form.addWidget(self._section_text("輸出檔名"))
        form.addWidget(self.output_name_edit)

        button_row = QHBoxLayout()
        self.generate_button = QPushButton("加入生成佇列")
        self.generate_button.setProperty("primary", True)
        self.regenerate_button = QPushButton("帶回右側設定")
        button_row.addWidget(self.generate_button, 1)
        button_row.addWidget(self.regenerate_button)
        form.addLayout(button_row)
        form.addStretch(1)

        scroll.setWidget(form_host)
        layout.addWidget(scroll, 1)
        return card

    def _build_center_panel(self) -> QWidget:
        card = self._create_card()
        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        section = QLabel("生成佇列")
        section.setProperty("section", True)
        layout.addWidget(section)

        self.active_job_title = QLabel("目前沒有執行中的任務")
        self.active_job_title.setStyleSheet("font-size: 13pt; font-weight: 700; color: #1f2f49;")
        self.active_job_status = QLabel("等待中")
        self.active_job_status.setStyleSheet("color: #5a6b88;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        cache_path = self.generator_service.model_cache_path()
        self.cache_path_label = QLabel(f"模型快取位置：{cache_path}")
        self.cache_path_label.setWordWrap(True)
        self.cache_path_label.setStyleSheet("color: #5a6b88;")

        layout.addWidget(self.active_job_title)
        layout.addWidget(self.active_job_status)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cache_path_label)

        queue_row = QHBoxLayout()
        queue_label = QLabel("等待中的任務")
        queue_label.setProperty("section", True)
        self.clear_queue_button = QPushButton("清空等待佇列")
        queue_row.addWidget(queue_label)
        queue_row.addStretch(1)
        queue_row.addWidget(self.clear_queue_button)
        layout.addLayout(queue_row)

        self.queue_list = QListWidget()
        self.queue_list.setMinimumHeight(200)
        layout.addWidget(self.queue_list)

        log_label = QLabel("系統訊息")
        log_label.setProperty("section", True)
        layout.addWidget(log_label)
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output, 1)
        return card

    def _build_right_panel(self) -> QWidget:
        card = self._create_card()
        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        section = QLabel("音檔庫")
        section.setProperty("section", True)
        self.refresh_button = QPushButton("重新整理")
        top_row.addWidget(section)
        top_row.addStretch(1)
        top_row.addWidget(self.refresh_button)
        layout.addLayout(top_row)

        self.library_table = QTableWidget(0, 3)
        self.library_table.setHorizontalHeaderLabels(["檔名", "時長", "建立時間"])
        self.library_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.library_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.library_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.library_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.library_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.library_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.library_table, 1)

        controls = QGridLayout()
        self.play_button = QPushButton("播放")
        self.pause_button = QPushButton("暫停")
        self.stop_button = QPushButton("停止")
        self.rename_button = QPushButton("更名")
        self.delete_button = QPushButton("刪除")
        self.open_folder_button = QPushButton("開啟資料夾")
        self.reuse_button = QPushButton("帶回設定")
        self.open_prompt_button = QPushButton("開啟提示詞檔")

        buttons = [
            self.play_button,
            self.pause_button,
            self.stop_button,
            self.rename_button,
            self.delete_button,
            self.open_folder_button,
            self.reuse_button,
            self.open_prompt_button,
        ]
        for index, button in enumerate(buttons):
            controls.addWidget(button, index // 2, index % 2)
        layout.addLayout(controls)

        self.track_meta_label = QLabel("選取右側音檔後，這裡會顯示中文參數摘要。")
        self.track_meta_label.setWordWrap(True)
        self.track_meta_label.setStyleSheet("color: #5a6b88;")
        layout.addWidget(self.track_meta_label)
        self.track_prompt_view = QPlainTextEdit()
        self.track_prompt_view.setReadOnly(True)
        self.track_prompt_view.setMinimumHeight(220)
        layout.addWidget(self.track_prompt_view)
        return card

    def _connect_signals(self) -> None:
        for widget in (
            self.style_combo,
            self.type_combo,
            self.mood_combo,
            self.key_combo,
            self.tonality_combo,
            self.complexity_combo,
            self.energy_combo,
            self.model_combo,
            self.duration_combo,
        ):
            widget.currentTextChanged.connect(self._update_prompt_preview)

        self.bpm_spin.valueChanged.connect(self._update_prompt_preview)
        self.loop_checkbox.toggled.connect(self._update_prompt_preview)
        self.seed_checkbox.toggled.connect(self._toggle_seed)
        self.seed_spin.valueChanged.connect(self._update_prompt_preview)
        self.prompt_boost_edit.textChanged.connect(self._update_prompt_preview)
        self.instrument_list.itemChanged.connect(self._update_prompt_preview)

        self.generate_button.clicked.connect(self._queue_generation)
        self.regenerate_button.clicked.connect(self._reuse_selected_track)
        self.refresh_button.clicked.connect(self._refresh_library)
        self.clear_queue_button.clicked.connect(self.generator_service.clear_pending_queue)

        self.generator_service.queue_changed.connect(self._render_queue)
        self.generator_service.job_progress.connect(self._handle_job_progress)
        self.generator_service.job_completed.connect(self._handle_job_completed)
        self.generator_service.job_failed.connect(self._handle_job_failed)
        self.generator_service.log_message.connect(self._append_log)
        self.generator_service.active_job_changed.connect(self._handle_active_job_changed)

        self.library_table.itemSelectionChanged.connect(self._show_selected_track_details)
        self.play_button.clicked.connect(self._play_selected_track)
        self.pause_button.clicked.connect(self.audio_preview_service.pause)
        self.stop_button.clicked.connect(self.audio_preview_service.stop)
        self.rename_button.clicked.connect(self._rename_selected_track)
        self.delete_button.clicked.connect(self._delete_selected_track)
        self.open_folder_button.clicked.connect(self._open_selected_folder)
        self.reuse_button.clicked.connect(self._reuse_selected_track)
        self.open_prompt_button.clicked.connect(self._open_selected_prompt)

        self.audio_preview_service.playback_state_changed.connect(self._update_playback_status)

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setProperty("card", True)
        card.setContentsMargins(0, 0, 0, 0)
        return card

    def _create_combo(self, options: list[ChoiceOption], default_token: str) -> QComboBox:
        combo = QComboBox()
        for option in options:
            combo.addItem(option.label, option.token)
        index = combo.findData(default_token)
        if index >= 0:
            combo.setCurrentIndex(index)
        return combo

    def _field_row(self, label_text: str, editor: QWidget, leading: QWidget | None = None) -> QWidget:
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        if leading is not None:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.addWidget(leading)
            row.addWidget(editor, 1)
            label = QLabel(label_text)
            label.setProperty("section", True)
            label.setStyleSheet("margin-top: 0px;")
            layout.addWidget(label)
            layout.addLayout(row)
            return host

        label = QLabel(label_text)
        label.setProperty("section", True)
        label.setStyleSheet("margin-top: 0px;")
        layout.addWidget(label)
        layout.addWidget(editor)
        return host

    def _section_text(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("section", True)
        label.setStyleSheet("margin-top: 0px;")
        return label

    def _toggle_seed(self, checked: bool) -> None:
        self.seed_spin.setEnabled(checked)
        self._update_prompt_preview()

    def _collect_form_data(self) -> PromptFormData:
        instrument_labels: list[str] = []
        instrument_tokens: list[str] = []
        for index in range(self.instrument_list.count()):
            item = self.instrument_list.item(index)
            if item.checkState() == Qt.Checked:
                instrument_labels.append(item.text())
                instrument_tokens.append(str(item.data(Qt.UserRole)))

        seed = self.seed_spin.value() if self.seed_checkbox.isChecked() else None
        return PromptFormData(
            style_label=self.style_combo.currentText(),
            style_token=str(self.style_combo.currentData()),
            type_label=self.type_combo.currentText(),
            type_token=str(self.type_combo.currentData()),
            instrument_labels=instrument_labels,
            instrument_tokens=instrument_tokens,
            mood_label=self.mood_combo.currentText(),
            mood_token=str(self.mood_combo.currentData()),
            bpm=self.bpm_spin.value(),
            key_label=self.key_combo.currentText(),
            key_token=str(self.key_combo.currentData()),
            tonality_label=self.tonality_combo.currentText(),
            tonality_token=str(self.tonality_combo.currentData()),
            duration_seconds=int(self.duration_combo.currentData()),
            loop_intent=self.loop_checkbox.isChecked(),
            complexity_label=self.complexity_combo.currentText(),
            complexity_token=str(self.complexity_combo.currentData()),
            energy_label=self.energy_combo.currentText(),
            energy_token=str(self.energy_combo.currentData()),
            model_label=self.model_combo.currentText(),
            model_token=str(self.model_combo.currentData()),
            seed=seed,
            prompt_boost=self.prompt_boost_edit.toPlainText().strip(),
        )

    def _update_prompt_preview(self) -> None:
        data = self._collect_form_data()
        self.prompt_preview_edit.blockSignals(True)
        self.prompt_preview_edit.setPlainText(build_prompt(data))
        self.prompt_preview_edit.blockSignals(False)

    def _queue_generation(self) -> None:
        issue = self.generator_service.environment_issue()
        if issue:
            QMessageBox.warning(self, "環境尚未準備完成", issue)
            return

        data = self._collect_form_data()
        final_prompt = self.prompt_preview_edit.toPlainText().strip()
        if not final_prompt:
            QMessageBox.warning(self, "提示詞為空", "請先產生或輸入一段可用的提示詞。")
            return

        filename = self.output_name_edit.text().strip() or suggested_filename(data)
        if not filename.lower().endswith(".wav"):
            filename = f"{filename}.wav"
        out_path = self._unique_output_path(self.music_dir / filename)
        metadata = build_metadata_sections(data, final_prompt)
        self.generator_service.enqueue_job(
            title=out_path.stem,
            prompt=final_prompt,
            out_path=out_path,
            seconds=data.duration_seconds,
            model=data.model_token,
            seed=data.seed,
            metadata=metadata,
        )
        self.statusBar().showMessage(f"已排入佇列：{out_path.name}")
        self.output_name_edit.clear()

    def _unique_output_path(self, candidate: Path) -> Path:
        if not candidate.exists():
            return candidate

        stem = candidate.stem
        suffix = candidate.suffix
        counter = 2
        while True:
            amended = candidate.with_name(f"{stem}-{counter}{suffix}")
            if not amended.exists():
                return amended
            counter += 1

    def _render_queue(self, jobs: list[GenerationJob]) -> None:
        self.queue_list.clear()
        for job in jobs:
            model_label = job.metadata.get("display", {}).get("模型", job.model)
            self.queue_list.addItem(f"{job.title}｜{job.seconds} 秒｜{model_label}")

    def _handle_active_job_changed(self, job: GenerationJob | None) -> None:
        if job is None:
            self.active_job_title.setText("目前沒有執行中的任務")
            self.active_job_status.setText("等待中")
            if self.progress_bar.value() < 100:
                self.progress_bar.setValue(0)
            return

        self.active_job_title.setText(job.title)
        model_label = job.metadata.get("display", {}).get("模型", job.model)
        self.active_job_status.setText(f"已開始：{job.seconds} 秒 / {model_label}")
        self.progress_bar.setValue(2)

    def _handle_job_progress(self, payload: dict) -> None:
        percent = int(payload.get("percent", 0))
        status = str(payload.get("status", "生成中"))
        job = payload.get("job")
        if isinstance(job, GenerationJob):
            self.active_job_title.setText(job.title)
        self.active_job_status.setText(status)
        self.progress_bar.setValue(percent)

    def _handle_job_completed(self, job: GenerationJob) -> None:
        self.progress_bar.setValue(100)
        self.active_job_title.setText(job.title)
        self.active_job_status.setText("已完成")
        self._append_log(f"完成：{job.out_path.name}")
        self.statusBar().showMessage(f"生成完成：{job.out_path.name}", 8000)
        self._refresh_library(select_path=job.out_path)
        self._sync_environment_banner()

    def _handle_job_failed(self, job: GenerationJob, details: str) -> None:
        self.active_job_title.setText(job.title)
        self.active_job_status.setText("失敗")
        self.progress_bar.setValue(0)
        self._append_log(f"失敗：{job.title}\n{details}")
        QMessageBox.critical(self, "生成失敗", details)
        self._sync_environment_banner()

    def _append_log(self, text: str) -> None:
        self.log_output.appendPlainText(text)

    def _refresh_library(self, *, select_path: Path | None = None) -> None:
        self.tracks = self.library_service.scan_tracks()
        self.library_table.setRowCount(len(self.tracks))
        for row, track in enumerate(self.tracks):
            self.library_table.setItem(row, 0, QTableWidgetItem(track.audio_path.name))
            self.library_table.setItem(row, 1, QTableWidgetItem(f"{track.duration_seconds:.1f} 秒"))
            self.library_table.setItem(row, 2, QTableWidgetItem(track.created_at.strftime("%Y-%m-%d %H:%M")))

        if select_path is not None:
            for row, track in enumerate(self.tracks):
                if track.audio_path == select_path:
                    self.library_table.selectRow(row)
                    break
        elif self.tracks and self.library_table.currentRow() < 0:
            self.library_table.selectRow(0)
        self._show_selected_track_details()

    def _selected_track(self) -> TrackRecord | None:
        row = self.library_table.currentRow()
        if row < 0 or row >= len(self.tracks):
            return None
        return self.tracks[row]

    def _show_selected_track_details(self) -> None:
        record = self._selected_track()
        if record is None:
            self.track_meta_label.setText("選取右側音檔後，這裡會顯示中文參數摘要。")
            self.track_prompt_view.clear()
            return

        display = dict(record.display_metadata)
        if not display:
            values = record.metadata.get("values", {})
            display = {
                "風格": label_for_token(STYLE_OPTIONS, values.get("style", "")),
                "類型": label_for_token(TYPE_OPTIONS, values.get("track_type", "")),
                "情緒": label_for_token(MOOD_OPTIONS, values.get("mood", "")),
                "節奏 / BPM": values.get("bpm", "-"),
                "模型": label_for_token(MODEL_OPTIONS, values.get("model", ""), values.get("model", "-")),
            }

        summary = [
            f"檔名：{record.audio_path.name}",
            f"時長：{record.duration_seconds:.1f} 秒",
            f"建立時間：{record.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"風格：{display.get('風格', '-')}",
            f"類型：{display.get('類型', '-')}",
            f"情緒：{display.get('情緒', '-')}",
            f"節奏 / BPM：{display.get('節奏 / BPM', '-')}",
            f"模型：{display.get('模型', record.metadata.get('model', '-'))}",
        ]
        self.track_meta_label.setText("｜".join(summary))

        final_prompt = record.metadata.get("final_prompt") or record.prompt_text or "（沒有提示詞）"
        meta_dump = json.dumps(record.metadata, ensure_ascii=False, indent=2) if record.metadata else "{}"
        self.track_prompt_view.setPlainText(f"{final_prompt}\n\n--- 詳細資料 ---\n{meta_dump}")

    def _play_selected_track(self) -> None:
        record = self._selected_track()
        if record is None:
            return
        self.audio_preview_service.play(record.audio_path)
        self.statusBar().showMessage(f"播放：{record.audio_path.name}")

    def _rename_selected_track(self) -> None:
        record = self._selected_track()
        if record is None:
            return
        new_name, accepted = QInputDialog.getText(self, "更名", "新的檔名（不含副檔名）", text=record.name)
        if not accepted:
            return
        try:
            updated = self.library_service.rename_track(record, new_name)
        except (ValueError, FileExistsError, FileNotFoundError) as exc:
            QMessageBox.warning(self, "更名失敗", str(exc))
            return
        self._refresh_library(select_path=updated.audio_path)
        self.statusBar().showMessage(f"已更名為：{updated.audio_path.name}", 5000)

    def _delete_selected_track(self) -> None:
        record = self._selected_track()
        if record is None:
            return
        answer = QMessageBox.question(
            self,
            "刪除音檔",
            f"確定要刪除 {record.audio_path.name} 與其對應的提示詞 / 詳細資料嗎？",
        )
        if answer != QMessageBox.Yes:
            return
        self.audio_preview_service.stop()
        self.library_service.delete_track(record)
        self._refresh_library()
        self.statusBar().showMessage(f"已刪除：{record.audio_path.name}", 5000)

    def _open_selected_folder(self) -> None:
        record = self._selected_track()
        if record is None:
            return
        self.library_service.open_in_explorer(record)

    def _reuse_selected_track(self) -> None:
        record = self._selected_track()
        if record is None:
            return
        values = record.metadata.get("values", {})
        if not values:
            QMessageBox.information(self, "缺少設定資料", "這首音檔沒有可重用的詳細資料。")
            return

        self._set_combo_by_token(self.style_combo, values.get("style"))
        self._set_combo_by_token(self.type_combo, values.get("track_type"))
        self._set_combo_by_token(self.mood_combo, values.get("mood"))
        self._set_combo_by_token(self.key_combo, values.get("key"))
        self._set_combo_by_token(self.tonality_combo, values.get("tonality"))
        self._set_combo_by_token(self.complexity_combo, values.get("complexity"))
        self._set_combo_by_token(self.energy_combo, values.get("energy"))
        self._set_combo_by_token(self.model_combo, values.get("model"))

        bpm = values.get("bpm")
        if isinstance(bpm, int):
            self.bpm_spin.setValue(bpm)

        duration = values.get("duration_seconds")
        if isinstance(duration, int):
            index = self.duration_combo.findData(duration)
            if index >= 0:
                self.duration_combo.setCurrentIndex(index)

        self.loop_checkbox.setChecked(bool(values.get("loop_intent", True)))
        seed = values.get("seed")
        self.seed_checkbox.setChecked(seed is not None)
        if isinstance(seed, int):
            self.seed_spin.setValue(seed)

        boost = values.get("prompt_boost", "")
        self.prompt_boost_edit.setPlainText(str(boost))

        selected = set(values.get("instruments", []))
        for index in range(self.instrument_list.count()):
            item = self.instrument_list.item(index)
            item.setCheckState(Qt.Checked if item.data(Qt.UserRole) in selected else Qt.Unchecked)

        final_prompt = record.metadata.get("final_prompt") or record.prompt_text
        self.prompt_preview_edit.setPlainText(final_prompt)
        self.statusBar().showMessage(f"已帶回設定：{record.audio_path.name}", 6000)

    def _open_selected_prompt(self) -> None:
        record = self._selected_track()
        if record is None or not record.prompt_path.exists():
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(record.prompt_path)))

    def _set_combo_by_token(self, combo: QComboBox, token: object) -> None:
        if token is None:
            return
        index = combo.findData(token)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _sync_environment_banner(self) -> None:
        issue = self.generator_service.environment_issue()
        cache_path = self.generator_service.model_cache_path()
        model_ready = self.generator_service.is_model_ready()
        if issue:
            self.environment_banner.setText(
                f"目前無法準備生成環境。\n{issue}\n模型快取位置：{cache_path}"
            )
            return

        if model_ready:
            self.environment_banner.setText(
                f"模型快取位置：{cache_path}\n目前已偵測到本機模型，可直接開始生成。"
            )
            return

        self.environment_banner.setText(
            f"模型快取位置：{cache_path}\n首次生成時會自動下載模型；若目前沒有網路，初始化會失敗。"
        )

    def _update_playback_status(self, state: str) -> None:
        state_mapping = {
            "PlayingState": "播放中",
            "PausedState": "已暫停",
            "StoppedState": "已停止",
        }
        self.statusBar().showMessage(f"播放器狀態：{state_mapping.get(state, state)}")

from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import scipy.io.wavfile
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

from app.core.runtime_paths import ensure_app_directories

TOKENS_PER_SECOND = 50.1
MAX_MUSICGEN_SECONDS = 30
MAX_NEW_TOKENS = 1503
DEFAULT_MODEL = "facebook/musicgen-small"

StatusCallback = Callable[[str], None]

_MODEL_CACHE: dict[tuple[str, str], tuple[AutoProcessor, MusicgenForConditionalGeneration, str]] = {}
_MODEL_LOCK = threading.Lock()


@dataclass
class GenerationSettings:
    prompt: str
    out_path: Path
    model: str = DEFAULT_MODEL
    seconds: int = 30
    guidance_scale: float = 3.0
    seed: Optional[int] = None
    cache_dir: Optional[Path] = None


@dataclass
class GenerationResult:
    audio_path: Path
    prompt_path: Path
    cache_dir: Path
    device: str
    model: str
    seconds: int
    downloaded_now: bool


def default_cache_dir() -> Path:
    return ensure_app_directories()["cache_dir"]


def is_model_cached(model_name: str, cache_dir: Optional[Path] = None) -> bool:
    target_cache = (cache_dir or default_cache_dir()).resolve()
    expected_folder = target_cache / f"models--{model_name.replace('/', '--')}"
    return expected_folder.exists()


def compute_max_new_tokens(seconds: int) -> int:
    clamped_seconds = max(1, min(MAX_MUSICGEN_SECONDS, seconds))
    return min(MAX_NEW_TOKENS, max(32, int(math.ceil(clamped_seconds * TOKENS_PER_SECOND))))


def generate_music(settings: GenerationSettings, status_callback: Optional[StatusCallback] = None) -> GenerationResult:
    prompt = settings.prompt.strip()
    if not prompt:
        raise ValueError("提示詞不可為空。")

    out_path = settings.out_path.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_output_path = out_path.with_suffix(".prompt.txt")

    cache_dir = (settings.cache_dir or default_cache_dir()).expanduser().resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_before = is_model_cached(settings.model, cache_dir)

    processor, model, device = _load_model(settings.model, cache_dir, cached_before, status_callback)

    if settings.seed is not None:
        torch.manual_seed(settings.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(settings.seed)

    if status_callback:
        status_callback("正在生成音訊，這通常會花一些時間。")

    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    )
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

    max_new_tokens = compute_max_new_tokens(settings.seconds)
    audio_values = model.generate(
        **inputs,
        do_sample=True,
        guidance_scale=settings.guidance_scale,
        max_new_tokens=max_new_tokens,
    )

    if status_callback:
        status_callback("正在寫入音檔與提示詞。")

    sampling_rate = model.config.audio_encoder.sampling_rate
    wav_data = _prepare_audio_for_wav(audio_values)
    scipy.io.wavfile.write(out_path, rate=sampling_rate, data=wav_data)
    prompt_output_path.write_text(f"{prompt}\n", encoding="utf-8")

    if status_callback:
        status_callback("音樂生成完成。")

    return GenerationResult(
        audio_path=out_path,
        prompt_path=prompt_output_path,
        cache_dir=cache_dir,
        device=device,
        model=settings.model,
        seconds=min(MAX_MUSICGEN_SECONDS, max(1, settings.seconds)),
        downloaded_now=not cached_before,
    )


def _load_model(
    model_name: str,
    cache_dir: Path,
    cached_before: bool,
    status_callback: Optional[StatusCallback],
) -> tuple[AutoProcessor, MusicgenForConditionalGeneration, str]:
    cache_key = (model_name, str(cache_dir))

    with _MODEL_LOCK:
        cached_model = _MODEL_CACHE.get(cache_key)
        if cached_model is not None:
            if status_callback:
                status_callback("已使用目前執行中的模型快取。")
            return cached_model

        if status_callback:
            if cached_before:
                status_callback("正在載入本機模型。")
            else:
                status_callback("首次初始化模型，正在下載到本機快取。")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            processor = AutoProcessor.from_pretrained(model_name, cache_dir=str(cache_dir))
            model = MusicgenForConditionalGeneration.from_pretrained(model_name, cache_dir=str(cache_dir))
            model.to(device)
        except Exception as exc:
            if cached_before:
                raise RuntimeError(f"載入模型失敗：{exc}") from exc
            raise RuntimeError(
                "模型尚未下載完成，且此次初始化失敗。請確認網路連線可用，或稍後再試。\n"
                f"原始錯誤：{exc}"
            ) from exc

        _MODEL_CACHE[cache_key] = (processor, model, device)
        return processor, model, device


def _prepare_audio_for_wav(audio_values: torch.Tensor) -> np.ndarray:
    audio = audio_values.detach().cpu().numpy()[0]
    if audio.ndim == 1:
        data = audio
    elif audio.shape[0] == 1:
        data = audio[0]
    else:
        data = np.transpose(audio, (1, 0))

    data = np.clip(data, -1.0, 1.0)
    return (data * 32767).astype(np.int16)

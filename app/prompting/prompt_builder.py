from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional


@dataclass(frozen=True)
class ChoiceOption:
    label: str
    token: str


STYLE_OPTIONS = [
    ChoiceOption("街機", "arcade"),
    ChoiceOption("低保真", "lofi"),
    ChoiceOption("電影感", "cinematic"),
    ChoiceOption("環境氛圍", "ambient"),
    ChoiceOption("晶片音樂", "chiptune"),
    ChoiceOption("合成波", "synthwave"),
    ChoiceOption("管弦", "orchestral"),
    ChoiceOption("驚悚", "horror"),
    ChoiceOption("奇幻", "fantasy"),
    ChoiceOption("賽博龐克", "cyberpunk"),
]

TYPE_OPTIONS = [
    ChoiceOption("背景音樂", "bgm"),
    ChoiceOption("循環片段", "loop"),
    ChoiceOption("戰鬥", "battle"),
    ChoiceOption("主選單", "menu"),
    ChoiceOption("勝利", "victory"),
    ChoiceOption("解謎", "puzzle"),
    ChoiceOption("探索", "exploration"),
    ChoiceOption("首領戰", "boss-like"),
    ChoiceOption("放鬆", "relax"),
]

INSTRUMENT_OPTIONS = [
    ChoiceOption("合成器", "synth"),
    ChoiceOption("鋼琴", "piano"),
    ChoiceOption("弦樂", "strings"),
    ChoiceOption("鼓組", "drums"),
    ChoiceOption("貝斯", "bass"),
    ChoiceOption("8-bit 主旋律", "8-bit lead"),
    ChoiceOption("鋪底音色", "pad"),
    ChoiceOption("撥弦音色", "pluck"),
    ChoiceOption("鐘聲", "bells"),
]

MOOD_OPTIONS = [
    ChoiceOption("明亮", "bright"),
    ChoiceOption("緊張", "tense"),
    ChoiceOption("陰暗", "dark"),
    ChoiceOption("溫暖", "warm"),
    ChoiceOption("振奮", "uplifting"),
    ChoiceOption("神秘", "mysterious"),
    ChoiceOption("高能量", "energetic"),
    ChoiceOption("平靜", "calm"),
]

KEY_OPTIONS = [ChoiceOption(label, label) for label in ["C", "D", "E", "F", "G", "A", "B"]]
TONALITY_OPTIONS = [ChoiceOption("大調", "major"), ChoiceOption("小調", "minor")]
COMPLEXITY_OPTIONS = [
    ChoiceOption("簡潔", "simple"),
    ChoiceOption("平衡", "balanced"),
    ChoiceOption("豐富", "rich"),
]
ENERGY_OPTIONS = [
    ChoiceOption("低", "low"),
    ChoiceOption("中", "medium"),
    ChoiceOption("高", "high"),
]
MODEL_OPTIONS = [ChoiceOption("本機 MusicGen Small", "facebook/musicgen-small")]
DURATION_OPTIONS = [4, 8, 12, 20, 30]


@dataclass
class PromptFormData:
    style_label: str
    style_token: str
    type_label: str
    type_token: str
    instrument_labels: list[str]
    instrument_tokens: list[str]
    mood_label: str
    mood_token: str
    bpm: int
    key_label: str
    key_token: str
    tonality_label: str
    tonality_token: str
    duration_seconds: int
    loop_intent: bool
    complexity_label: str
    complexity_token: str
    energy_label: str
    energy_token: str
    model_label: str
    model_token: str
    seed: Optional[int]
    prompt_boost: str


def build_prompt(data: PromptFormData) -> str:
    instrument_text = ", ".join(data.instrument_tokens) if data.instrument_tokens else "synth"
    loop_text = "seamless loop" if data.loop_intent else "self-contained game cue"
    clauses = [
        f"{data.style_token} {data.type_token} game background music",
        "instrumental only",
        loop_text,
        "no vocals",
        "no spoken words",
        "no dramatic intro",
        "no fade-out outro",
        f"{data.complexity_token} arrangement",
        f"{data.energy_token} energy",
        f"{data.mood_token} mood",
        f"around {data.bpm} BPM",
        f"in {data.key_token} {data.tonality_token}",
        f"featuring {instrument_text}",
    ]

    prompt = ", ".join(clauses)
    if data.prompt_boost.strip():
        prompt = f"{prompt}, {data.prompt_boost.strip()}"
    return f"{prompt}."


def suggested_filename(data: PromptFormData) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    style_slug = slugify(data.style_token)
    type_slug = slugify(data.type_token)
    return f"{timestamp}-{style_slug}-{type_slug}-{data.bpm}bpm.wav"


def build_metadata_sections(data: PromptFormData, final_prompt: str) -> dict:
    return {
        "display": {
            "風格": data.style_label,
            "類型": data.type_label,
            "樂器": data.instrument_labels,
            "情緒": data.mood_label,
            "節奏 / BPM": data.bpm,
            "調性主音": data.key_label,
            "大小調": data.tonality_label,
            "時長": data.duration_seconds,
            "循環意圖": "是" if data.loop_intent else "否",
            "編曲複雜度": data.complexity_label,
            "能量感": data.energy_label,
            "模型": data.model_label,
            "固定 Seed": data.seed,
            "補強描述": data.prompt_boost,
        },
        "values": {
            "style": data.style_token,
            "track_type": data.type_token,
            "instruments": data.instrument_tokens,
            "mood": data.mood_token,
            "bpm": data.bpm,
            "key": data.key_token,
            "tonality": data.tonality_token,
            "duration_seconds": data.duration_seconds,
            "loop_intent": data.loop_intent,
            "complexity": data.complexity_token,
            "energy": data.energy_token,
            "model": data.model_token,
            "seed": data.seed,
            "prompt_boost": data.prompt_boost,
        },
        "final_prompt": final_prompt,
    }


def find_option_by_label(options: Iterable[ChoiceOption], label: str) -> ChoiceOption | None:
    for option in options:
        if option.label == label:
            return option
    return None


def find_option_by_token(options: Iterable[ChoiceOption], token: str) -> ChoiceOption | None:
    for option in options:
        if option.token == token:
            return option
    return None


def label_for_token(options: Iterable[ChoiceOption], token: str, fallback: str = "-") -> str:
    option = find_option_by_token(options, token)
    return option.label if option is not None else fallback


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "track"

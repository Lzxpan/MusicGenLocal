import argparse
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.musicgen_engine import (
    DEFAULT_MODEL,
    MAX_MUSICGEN_SECONDS,
    GenerationSettings,
    generate_music,
)

DEFAULT_OUTPUT_PATH = REPO_ROOT / "music" / "bgm-loop.wav"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate loop-friendly background music locally with MusicGen."
    )
    parser.add_argument("--prompt", help="Inline text prompt.")
    parser.add_argument("--prompt-file", help="Path to a text prompt file.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--guidance-scale", type=float, default=3.0)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cache-dir", help="Optional model cache directory.")
    return parser.parse_args()


def load_prompt(args):
    if args.prompt:
        return args.prompt.strip()

    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()

    raise ValueError("Provide --prompt or --prompt-file.")

def main():
    args = parse_args()
    prompt = load_prompt(args)
    if not prompt:
        raise ValueError("提示詞不可為空。")

    if args.seconds > MAX_MUSICGEN_SECONDS:
        print(f"要求 {args.seconds} 秒，已限制為 {MAX_MUSICGEN_SECONDS} 秒，因為 MusicGen 最多支援 30 秒。")

    result = generate_music(
        GenerationSettings(
            prompt=prompt,
            out_path=Path(args.out),
            model=args.model,
            seconds=args.seconds,
            guidance_scale=args.guidance_scale,
            seed=args.seed,
            cache_dir=Path(args.cache_dir) if args.cache_dir else None,
        ),
        status_callback=print,
    )
    print(f"音檔已儲存：{result.audio_path}")
    print(f"提示詞已儲存：{result.prompt_path}")
    print(f"模型：{result.model}")
    print(f"裝置：{result.device}")
    print(f"模型快取位置：{result.cache_dir}")
    print(f"音樂長度：{result.seconds} 秒")
    if result.downloaded_now:
        print("此次已完成首次模型初始化。")


if __name__ == "__main__":
    main()

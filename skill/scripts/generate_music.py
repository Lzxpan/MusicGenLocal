import argparse
import math
import os
from pathlib import Path

import numpy as np
import scipy.io.wavfile
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

TOKENS_PER_SECOND = 50.1
MAX_MUSICGEN_SECONDS = 30
MAX_NEW_TOKENS = 1503
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[2] / "music" / "bgm-loop.wav"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate loop-friendly background music locally with MusicGen."
    )
    parser.add_argument("--prompt", help="Inline text prompt.")
    parser.add_argument("--prompt-file", help="Path to a text prompt file.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--model", default="facebook/musicgen-small")
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--guidance-scale", type=float, default=3.0)
    parser.add_argument("--seed", type=int)
    return parser.parse_args()


def load_prompt(args):
    if args.prompt:
        return args.prompt.strip()

    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()

    raise ValueError("Provide --prompt or --prompt-file.")


def compute_max_new_tokens(seconds):
    clamped_seconds = max(1, min(MAX_MUSICGEN_SECONDS, seconds))
    return min(MAX_NEW_TOKENS, max(32, int(math.ceil(clamped_seconds * TOKENS_PER_SECOND))))


def prepare_audio_for_wav(audio_values):
    audio = audio_values.detach().cpu().numpy()[0]
    if audio.ndim == 1:
        data = audio
    elif audio.shape[0] == 1:
        data = audio[0]
    else:
        data = np.transpose(audio, (1, 0))

    data = np.clip(data, -1.0, 1.0)
    return (data * 32767).astype(np.int16)


def main():
    args = parse_args()
    prompt = load_prompt(args)
    if not prompt:
        raise ValueError("Prompt text is empty.")

    if args.seconds > MAX_MUSICGEN_SECONDS:
        print(f"Requested {args.seconds}s, clamping to {MAX_MUSICGEN_SECONDS}s because MusicGen supports up to 30s.")

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_output_path = out_path.with_suffix(".prompt.txt")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained(args.model)
    model = MusicgenForConditionalGeneration.from_pretrained(args.model)
    model.to(device)

    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    )
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

    if args.seed is not None:
        torch.manual_seed(args.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(args.seed)

    max_new_tokens = compute_max_new_tokens(args.seconds)
    audio_values = model.generate(
        **inputs,
        do_sample=True,
        guidance_scale=args.guidance_scale,
        max_new_tokens=max_new_tokens,
    )

    sampling_rate = model.config.audio_encoder.sampling_rate
    wav_data = prepare_audio_for_wav(audio_values)

    scipy.io.wavfile.write(out_path, rate=sampling_rate, data=wav_data)
    prompt_output_path.write_text(f"{prompt}\n", encoding="utf-8")

    print(f"Audio saved to {out_path}")
    print(f"Prompt saved to {prompt_output_path}")
    print(f"Model: {args.model}")
    print(f"Device: {device}")
    print(f"Seconds requested: {min(MAX_MUSICGEN_SECONDS, max(1, args.seconds))}")


if __name__ == "__main__":
    main()

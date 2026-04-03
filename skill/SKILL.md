---
name: musicgen-local
description: Generate local background music and loopable game BGM with Meta MusicGen on the user's machine. Use when Codex needs an offline or no-API music generation workflow, especially for game soundtrack prototyping, seamless loop-style prompts, local setup of Python dependencies, or repeated text-to-music generation after cloud APIs are unavailable, paid, or quota-limited.
---

# MusicGen Local

Use the bundled scripts to set up a dedicated Python environment and generate `.wav` music locally with `facebook/musicgen-small`.

## Quick Start

1. Run `scripts/setup_venv.ps1` to create `.venv` and install dependencies.
2. Run `scripts/generate_music.py` with either `--prompt` or `--prompt-file`.
3. Save outputs to a temp path first while iterating.
4. For loopable BGM, keep prompts explicit and render short tests before committing to 30 seconds.

## Workflow

1. Prefer 4-12 second renders while iterating on prompt wording.
2. Use `--seconds 30` only after the prompt already produces the right texture and pacing.
3. Keep prompts instrumental and loop-oriented:
   `instrumental only`, `seamless loop`, `no vocals`, `no spoken words`, `no dramatic intro`, `no fade-out outro`.
4. Write outputs as `.wav` and audition them manually; MusicGen does not guarantee mathematically perfect loop points.
5. Save the final chosen prompt next to the output for reproducibility.

## Commands

Set up the environment:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\scripts\setup_venv.ps1
```

Generate from a prompt file:

```powershell
C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\.venv\Scripts\python.exe C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\scripts\generate_music.py --prompt-file C:\path\to\prompt.txt --out C:\Temp\music-loop.wav --seconds 8
```

Generate from inline prompt text:

```powershell
C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\.venv\Scripts\python.exe C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\scripts\generate_music.py --prompt "Retro arcade puzzle game loop, instrumental only, seamless loop, no vocals." --out C:\Temp\music-loop.wav --seconds 8
```

## Resources

- `scripts/setup_venv.ps1`: create `.venv` and install required Python packages.
- `scripts/generate_music.py`: render `.wav` music locally from text prompts.
- `references/prompting.md`: prompt patterns for loopable game music.

Read `references/prompting.md` when you need to craft or revise prompts for arcade loops, lofi loops, or other reusable game BGM.


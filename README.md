# Flux

**Flux** is a clean, intuitive Python CLI wrapper for the OpenRouter API that makes conversational AI interactions effortless. It manages context across persistent chat sessions, saves prompt/response exchanges as markdown files, and supports customizable model and tone presets via TOML configuration — a flexible, playful framework for quality LLM interfacing.

## Two versions of this project

This repo has two branches, and they differ on purpose:

- **`main`** — the original FluxWrap, frozen at tag `v0-jank`. `fluxwrap.py` as first written: fully working, but with no input validation (a stray keystroke at a menu crashes the session). Kept as-is for posterity. To see it: `git checkout main` or `git checkout v0-jank`.
- **`flux`** (you are here) — the hardened fork. Same program, renamed to `flux.py`, with crash-proof input handling and a session salvage net. All new work happens on this branch.

To switch back: `git checkout main`. To return: `git checkout flux`.

## What's different on this branch

- **Renamed** `fluxwrap.py` → `flux.py`.
- **Input validation everywhere.** Menu choices (model, tone) re-ask on junk or out-of-range input instead of crashing. Max Tokens and Temperature prompts keep the current value on Enter, re-ask on garbage, and bail on X.
- **Crash salvage.** If anything unexpected kills the program, the conversation so far is dumped to `CRASH_<timestamp>_<model>_<tone>.md` in your save directory instead of being lost. Ctrl-C / Ctrl-D exit cleanly.
- **Per-model parameter reset.** Temperature and Max Tokens start from your TOML defaults each time you pick a model, instead of leaking across models within a run.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (gitignored — never commit it):

```
API_KEY=sk-or-...           # your OpenRouter key
SAVE_DIR=~/path/to/logs     # where session logs land
PRIVATE_CONFIG=~/path/to/flux_private.toml   # your private tones/models
```

`flux_private.toml` (also gitignored) merges over `flux_config.toml` at startup — same `[models]` / `[tones]` shape. Your private entries appear in the menus alongside the defaults.

## Usage

```bash
source .venv/bin/activate
python flux.py
```

1. **Pick a model** from the numbered menu (X to quit).
2. **Pick a mode:** `0` (or Enter) for a persistent session, `1` for a single one-shot prompt.
3. Session mode asks for a **tone** (system prompt preset; Enter for default), then loops: prompt → Max Tokens → Temperature → payload preview → confirm → response rendered as markdown.
4. After each exchange you can **save to file**: sessions append to `SAVE_DIR/<TONE>/<YYYY-MM-DD>_<tone>.md`, single shots to `SAVE_DIR/<model>_log.md`. Newest entries are prepended.

## Configuration

`flux_config.toml` holds everything:

- `[meta]` — default `temperature` and `max_tokens`.
- `[models]` — OpenRouter callstrings mapped to display names with pricing per 1M tokens (input/output). Menu order follows file order; add new models at the bottom.
- `[tones]` — named system-prompt presets (tutor, writer, critic, tarot, ...). Tone `default` is no system prompt.

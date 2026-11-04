# Carver Weather Desk

Pipeline for the YouTube weather-news channel **Carver Weather Desk** (@CarverWeatherDesk).

- **Host:** Glenn Carver, an AI avatar rendered in HeyGen.
- **Separate from IWN** (`../worflow.md`). The two channels share only research, footage sourcing and weather-data tools.

## How an episode is made

1. **The owner** gives a topic, sometimes with clips.
2. **Research, footage and script.** We research it, scout footage and write **ONE HeyGen script** (`script/heygen_paste.txt`). The finished video is **12:00 at most**.
3. **The owner** renders it in HeyGen as one continuous video, saved as `episodes/<ep>/host/glenn_raw.mp4`.
4. **The pipeline** builds the finished MP4 and an editable CapCut draft.

Where to find the rules:
- Full process: [workflow.md](workflow.md)
- Script rules: [docs/script-guide.md](docs/script-guide.md)
- Card specs: [docs/cards.md](docs/cards.md)
- Edit formats: [docs/timeline-schema.md](docs/timeline-schema.md)

## Setup (once per machine)

- **System:** Windows 10/11, Python 3.12, and `ffmpeg` on PATH. Use a full build with `libx264` and `prores_ks`.
  - NVIDIA NVENC is used when the GPU has it, otherwise libx264.
  - `CARVER_ENCODER=cpu` forces the CPU.
- **Install:**
  - `pip install -r requirements.txt`
  - `python -m playwright install chromium`
- **GPU speech sync (optional, NVIDIA):** `pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12>=9,<10"`.
  - Without it, `align_host.py` runs on the CPU at about 2× real time.
- **Brand kit, once:** `python pipeline/make_brand_motion.py`.
  - It renders `brand-kit/graphics`, `brand-kit/motion` and `brand-kit/sfx` in about 3 minutes.
  - These are generated files and are not in git.
- **CapCut desktop:** drafts are written to `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft`.

## Per episode (run from `pipeline/`, `<ep>` = `../episodes/<YYYY-MM-DD-slug>`)

```
python script_tools.py build <ep>        # lint + the ONE HeyGen script (fails over 12:00)
# owner renders HeyGen -> <ep>/host/glenn_raw.mp4
python prep_host.py <ep>                 # host crops + voice at -16 LUFS
python align_host.py <ep>                # word-level sync of the script to Glenn's voice
#   write card specs in <ep>/graphics/cards/<id>.json (docs/cards.md)
python plan_edit.py <ep> --render        # timeline + cards, straps, CTAs, ticker, base shots
python compose.py <ep> --sheet           # final MP4 + QC sheet
python build_capcut.py <ep>              # CapCut draft (same timeline)
```

## Not in git

- `episodes/`: footage, HeyGen renders and exports stay local.
- `brand-kit/graphics`, `motion` and `sfx`: regenerate them with `make_brand_motion.py`.
- Review renders (`brand-kit/styleframes`, `brand-kit/logo`) and Glenn's source photos.
- The YuNet face model: `prep_host.py` downloads it on first use.

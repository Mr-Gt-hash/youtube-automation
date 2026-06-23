# 🎬 YouTube Automation Pipeline

> A fully automated, end-to-end YouTube content pipeline — from niche research to publishing — powered by AI, Python, and cloud tools.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📌 Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
- [Scheduling](#scheduling)
- [CI/CD](#cicd)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project automates the **entire YouTube content creation cycle**:

1. **Niche & Trend Research** — Auto-discovers trending topics using Google Trends + YouTube Data API
2. **Script Generation** — AI-written scripts via OpenAI GPT-4
3. **Voiceover Synthesis** — Text-to-speech via ElevenLabs / Google TTS
4. **Thumbnail Creation** — Auto-generated thumbnails with Pillow + DALL·E
5. **Video Assembly** — MoviePy stitches clips, voiceover, captions & music
6. **SEO Metadata** — Auto-generates titles, descriptions, tags
7. **Upload & Publish** — Schedules and uploads via YouTube Data API v3
8. **Analytics Monitoring** — Tracks views, CTR, watch time and alerts on spikes

---

## Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     YouTube Automation Pipeline                      │
│                                                                      │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │   Niche &   │───▶│    Script    │───▶│  Voiceover (TTS)    │   │
│  │   Trends    │    │  Generator   │    │  ElevenLabs / gTTS   │   │
│  └─────────────┘    └──────────────┘    └──────────────────────┘   │
│         │                                           │               │
│         ▼                                           ▼               │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  Thumbnail  │    │    Video     │◀───│    B-Roll / Assets   │   │
│  │  Generator  │───▶│   Assembler  │    │    (Pexels API)      │   │
│  └─────────────┘    └──────────────┘    └──────────────────────┘   │
│                             │                                       │
│                             ▼                                       │
│                    ┌──────────────┐    ┌──────────────────────┐   │
│                    │  SEO Meta    │───▶│  Upload & Scheduler  │   │
│                    │  Generator   │    │  YouTube Data API v3  │   │
│                    └──────────────┘    └──────────────────────┘   │
│                                                   │               │
│                                                   ▼               │
│                                        ┌──────────────────────┐   │
│                                        │  Analytics Monitor   │   │
│                                        │  + Slack / Email     │   │
│                                        └──────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Features

- 🔍 Auto-discovers trending niches via Google Trends & YouTube search
- 📝 GPT-4 powered script writing with hooks, CTAs, and chapters
- 🎙️ ElevenLabs voice cloning or Google TTS fallback
- 🖼️ Thumbnail auto-generated with face + text overlay (A/B variants)
- 🎬 Full video compilation with captions, background music, transitions
- 🏷️ SEO-optimized titles, descriptions, and 30+ tags per video
- 📅 Smart upload scheduler (best time-to-post detection)
- 📊 Post-publish analytics dashboard with Slack/email alerts
- 🔄 GitHub Actions CI/CD for automated daily runs
- 🔐 Full secrets management via `.env`

---

## Folder Structure

```
youtube-automation/
├── src/
│   ├── niche_research/
│   │   ├── trends_scraper.py       # Google Trends + YouTube trending
│   │   └── keyword_analyzer.py     # Competition & volume scoring
│   ├── script_generator/
│   │   ├── gpt_writer.py           # GPT-4 script generation
│   │   └── prompt_templates.py     # Modular prompt library
│   ├── voiceover/
│   │   ├── tts_engine.py           # ElevenLabs / gTTS wrapper
│   │   └── audio_processor.py      # Normalisation, noise reduction
│   ├── thumbnail/
│   │   ├── generator.py            # Pillow thumbnail builder
│   │   └── dalle_variant.py        # DALL·E background generation
│   ├── video_editor/
│   │   ├── assembler.py            # MoviePy video assembly
│   │   ├── caption_burner.py       # Auto-captions from transcript
│   │   └── music_mixer.py          # Royalty-free BGM mixer
│   ├── uploader/
│   │   ├── youtube_client.py       # YouTube Data API v3 wrapper
│   │   └── seo_generator.py        # Title/desc/tags generator
│   ├── scheduler/
│   │   └── job_scheduler.py        # APScheduler cron jobs
│   └── analytics/
│       ├── tracker.py              # Pulls analytics from YT API
│       └── notifier.py             # Slack/email alerting
├── config/
│   ├── settings.py                 # Central config loader
│   └── prompts.yaml                # Editable prompt templates
├── tests/
│   ├── test_script_generator.py
│   ├── test_uploader.py
│   └── test_thumbnail.py
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml      # GitHub Actions daily run
├── logs/                           # Auto-created runtime logs
├── main.py                         # Pipeline entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- FFmpeg installed (`sudo apt install ffmpeg` or `brew install ffmpeg`)
- A Google Cloud Project with YouTube Data API v3 enabled
- OpenAI API key
- ElevenLabs API key (optional, gTTS fallback included)
- Pexels API key (for B-roll footage)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/youtube-automation.git
cd youtube-automation

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in your API keys in .env
```

---

## Configuration

Edit `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# ElevenLabs (optional)
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# YouTube OAuth
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...

# Pexels B-Roll
PEXELS_API_KEY=...

# Notifications
SLACK_WEBHOOK_URL=...
ALERT_EMAIL=you@example.com

# Pipeline settings
TARGET_NICHE=technology
VIDEOS_PER_DAY=1
UPLOAD_TIME=17:00         # 5 PM publish
VIDEO_LANGUAGE=en
MAX_VIDEO_DURATION=600    # 10 minutes
```

---

## Usage

### Run full pipeline once

```bash
python main.py
```

### Run individual modules

```bash
# Research only
python -m src.niche_research.trends_scraper

# Generate script for a topic
python -m src.script_generator.gpt_writer --topic "Best Python libraries 2025"

# Upload a pre-made video
python -m src.uploader.youtube_client --file output/video.mp4 --meta output/meta.json
```

### Run with scheduler (daemon mode)

```bash
python -m src.scheduler.job_scheduler
```

---

## Modules

### 1. Niche Research (`src/niche_research/`)

Discovers trending topics in your niche using:
- **Google Trends** (via `pytrends`) for rising keywords
- **YouTube Data API** `search.list` for viral videos in your category
- Scores topics by: search volume, competition, monetisation potential

### 2. Script Generator (`src/script_generator/`)

Uses GPT-4 with structured prompts to write:
- Hook (first 30 seconds)
- Main content with chapters
- CTA (subscribe, like, comment prompts)
- End screen script
- Description + tags in same call

### 3. Voiceover (`src/voiceover/`)

Primary: ElevenLabs API with your cloned voice  
Fallback: Google Text-to-Speech (free)  
Post-processing: normalisation, silence trimming, background noise reduction

### 4. Thumbnail (`src/thumbnail/`)

- Generates 2 A/B thumbnail variants per video
- Text overlay with bold typography (Impact font)
- Optional DALL·E background generation
- Outputs 1280×720 JPG at <2MB for YouTube spec

### 5. Video Assembler (`src/video_editor/`)

- Fetches relevant B-roll from Pexels API
- Stitches clips with voiceover timing
- Burns in auto-captions (from Whisper transcript)
- Mixes royalty-free background music at –18dB
- Renders final MP4 (H.264, 1080p)

### 6. Uploader (`src/uploader/`)

- Authenticates with YouTube OAuth 2.0
- Uploads video with full metadata
- Sets thumbnail, category, playlist, tags
- Schedules publish time (not immediately public)

### 7. Analytics Monitor (`src/analytics/`)

Polls YouTube Analytics API every 6 hours:
- Tracks views, watch time, CTR, subscriber delta
- Fires Slack alert if CTR > 8% (viral signal)
- Writes daily CSV report to `logs/`

---

## Scheduling

The scheduler uses **APScheduler** and runs as a daemon:

| Job | Schedule | Description |
|-----|----------|-------------|
| Full pipeline | Daily 09:00 | Research → Script → Video → Upload |
| Analytics pull | Every 6h | Fetch latest metrics |
| Niche refresh | Weekly Mon | Re-score topic database |

Alternatively use GitHub Actions (see below) for zero-server operation.

---

## CI/CD

`.github/workflows/daily_pipeline.yml` runs the full pipeline on GitHub Actions every day at 09:00 UTC using repository secrets.

To activate:
1. Add your API keys as **GitHub Repository Secrets** (Settings → Secrets → Actions)
2. Enable the workflow in the Actions tab
3. The pipeline will run automatically — no server needed

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-module`)
3. Commit changes (`git commit -m 'Add my module'`)
4. Push and open a Pull Request

---

## License

MIT License — free to use, modify, and distribute.

---

> Built with ❤️ for creators who'd rather automate than edit.

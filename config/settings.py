"""Central configuration — loads from .env and validates required keys."""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # ── OpenAI ──────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    OPENAI_MODEL: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))

    # ── ElevenLabs ──────────────────────────────────────────────────────────────
    ELEVENLABS_API_KEY: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    ELEVENLABS_VOICE_ID: str = field(default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ID", ""))

    # ── YouTube ──────────────────────────────────────────────────────────────────
    YOUTUBE_CLIENT_ID: str = field(default_factory=lambda: os.getenv("YOUTUBE_CLIENT_ID", ""))
    YOUTUBE_CLIENT_SECRET: str = field(default_factory=lambda: os.getenv("YOUTUBE_CLIENT_SECRET", ""))
    YOUTUBE_REFRESH_TOKEN: str = field(default_factory=lambda: os.getenv("YOUTUBE_REFRESH_TOKEN", ""))

    # ── Pexels ───────────────────────────────────────────────────────────────────
    PEXELS_API_KEY: str = field(default_factory=lambda: os.getenv("PEXELS_API_KEY", ""))

    # ── Notifications ────────────────────────────────────────────────────────────
    SLACK_WEBHOOK_URL: str = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL", ""))
    ALERT_EMAIL: str = field(default_factory=lambda: os.getenv("ALERT_EMAIL", ""))

    # ── Pipeline ─────────────────────────────────────────────────────────────────
    TARGET_NICHE: str = field(default_factory=lambda: os.getenv("TARGET_NICHE", "technology"))
    VIDEOS_PER_DAY: int = field(default_factory=lambda: int(os.getenv("VIDEOS_PER_DAY", "1")))
    UPLOAD_TIME: str = field(default_factory=lambda: os.getenv("UPLOAD_TIME", "17:00"))
    VIDEO_LANGUAGE: str = field(default_factory=lambda: os.getenv("VIDEO_LANGUAGE", "en"))
    MAX_VIDEO_DURATION: int = field(default_factory=lambda: int(os.getenv("MAX_VIDEO_DURATION", "600")))
    VIDEO_CATEGORY_ID: str = field(default_factory=lambda: os.getenv("VIDEO_CATEGORY_ID", "28"))  # 28 = Science & Tech

    def validate(self):
        required = ["OPENAI_API_KEY", "YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
        missing = [k for k in required if not getattr(self, k)]
        if missing:
            raise EnvironmentError(f"Missing required env vars: {missing}")
        return self

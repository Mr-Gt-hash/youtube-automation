"""
Script Generator — uses GPT-4 to write full YouTube scripts with hooks,
chapters, CTAs, and auto-generates SEO metadata in one API call.
"""

import json
import logging
from pathlib import Path
from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert YouTube scriptwriter and SEO specialist.
Write engaging, educational scripts optimised for watch time and audience retention.
Always follow this structure: Hook → Problem → Solution → Steps → CTA → Outro.
Return ONLY valid JSON, no markdown fences."""

SCRIPT_TEMPLATE = """Write a complete YouTube script for the topic: "{topic}"

Requirements:
- Video length: {duration} seconds (approx {words} words at 150 wpm)
- Language: {language}
- Tone: conversational, enthusiastic, expert
- Include: strong hook (first 30s), chapter timestamps, subscribe CTA, end screen prompt

Return JSON with these exact keys:
{{
  "title": "SEO-optimised video title (max 70 chars)",
  "narration": "Full narration script as a single string",
  "chapters": [{{"time": "0:00", "title": "Intro"}}, ...],
  "hook": "First 30 seconds of narration",
  "cta": "Subscribe/like/comment call-to-action text",
  "description": "YouTube description (500-700 words, SEO-rich)",
  "tags": ["tag1", "tag2", ...],
  "thumbnail_text": "3-5 word thumbnail headline"
}}"""


class ScriptWriter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.OPENAI_API_KEY)

    def generate(self, topic: str) -> dict:
        """Generate a complete script for the given topic."""
        logger.info(f"Generating script for: '{topic}'")

        duration = self.cfg.MAX_VIDEO_DURATION
        words = int(duration / 60 * 150)

        prompt = SCRIPT_TEMPLATE.format(
            topic=topic,
            duration=duration,
            words=words,
            language=self.cfg.VIDEO_LANGUAGE,
        )

        response = self.client.chat.completions.create(
            model=self.cfg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        raw = response.choices[0].message.content
        script = json.loads(raw)
        script["topic"] = topic
        logger.info(f"Script generated: '{script.get('title', topic)}'")
        return script

    def save(self, script: dict, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(script, indent=2, ensure_ascii=False))
        logger.info(f"Script saved → {path}")

"""
SEO Generator — enriches and finalises video metadata (title, description, tags)
using the script content already produced by GPT.
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

TITLE_MAX = 70
TAG_MAX = 500   # YouTube total tag character limit


class SEOGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def generate(self, script: dict, topic: str) -> dict:
        """Build final metadata dict from script output."""
        title = self._clean_title(script.get("title", topic))
        description = self._build_description(script, topic)
        tags = self._build_tags(script, topic)

        metadata = {
            "title": title,
            "description": description,
            "tags": tags,
            "topic": topic,
            "chapters": script.get("chapters", []),
        }
        logger.info(f"SEO metadata ready: '{title}' | {len(tags)} tags")
        return metadata

    def _clean_title(self, title: str) -> str:
        title = re.sub(r'[<>"\']', "", title).strip()
        return title[:TITLE_MAX]

    def _build_description(self, script: dict, topic: str) -> str:
        desc_parts = [script.get("description", "")]

        # Append chapter timestamps
        chapters = script.get("chapters", [])
        if chapters:
            desc_parts.append("\n\n📌 CHAPTERS")
            for ch in chapters:
                desc_parts.append(f"{ch.get('time', '0:00')} — {ch.get('title', '')}")

        # Standard footer
        desc_parts.append(
            f"\n\n🔔 Subscribe for more {topic} content!"
            "\n👍 Like if this helped you!"
            "\n💬 Drop your questions in the comments.\n\n"
            "#YouTube #Automation #AI"
        )

        full = "\n".join(desc_parts)
        return full[:5000]  # YouTube description limit

    def _build_tags(self, script: dict, topic: str) -> list[str]:
        raw_tags = script.get("tags", [])
        # Add topic variants
        extra = [topic, f"{topic} tutorial", f"{topic} 2025", "how to", "tutorial", "AI", "automation"]
        all_tags = list(dict.fromkeys(raw_tags + extra))  # deduplicate, preserve order

        # Trim to YouTube's 500-char aggregate limit
        selected, total = [], 0
        for tag in all_tags:
            if total + len(tag) + 1 > TAG_MAX:
                break
            selected.append(tag)
            total += len(tag) + 1

        return selected

    def save(self, metadata: dict, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

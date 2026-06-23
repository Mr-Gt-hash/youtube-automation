"""
Thumbnail Generator — creates 1280×720 YouTube thumbnails with
bold text overlay, background image (Pexels or DALL·E), and branding.
"""

import logging
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

THUMB_W, THUMB_H = 1280, 720
FONT_SIZE_LARGE = 96
FONT_SIZE_SMALL = 52


class ThumbnailGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def generate_variants(self, title: str, output_dir: Path, variants: int = 2) -> list[Path]:
        """Generate N thumbnail variants and return their paths."""
        paths = []
        for i in range(variants):
            bg = self._fetch_background(title, variant=i)
            thumb = self._compose(bg, title, variant=i)
            out = output_dir / f"thumbnail_v{i+1}.jpg"
            thumb.save(str(out), "JPEG", quality=95, optimize=True)
            logger.info(f"Thumbnail {i+1} saved → {out}")
            paths.append(out)
        return paths

    def _fetch_background(self, query: str, variant: int) -> Image.Image:
        """Fetch a background image from Pexels."""
        try:
            headers = {"Authorization": self.cfg.PEXELS_API_KEY}
            page = variant + 1
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params={"query": query, "per_page": 1, "page": page, "orientation": "landscape"},
                timeout=10,
            )
            r.raise_for_status()
            url = r.json()["photos"][0]["src"]["original"]
            img_data = requests.get(url, timeout=15).content
            img = Image.open(BytesIO(img_data)).convert("RGB")
            return img.resize((THUMB_W, THUMB_H), Image.LANCZOS)
        except Exception as e:
            logger.warning(f"Background fetch failed ({e}), using gradient")
            return self._gradient_background(variant)

    def _gradient_background(self, variant: int) -> Image.Image:
        """Fallback: a dark-blue gradient."""
        img = Image.new("RGB", (THUMB_W, THUMB_H))
        colors = [(10, 10, 40), (30, 80, 160)] if variant == 0 else [(20, 10, 10), (160, 40, 30)]
        draw = ImageDraw.Draw(img)
        for y in range(THUMB_H):
            ratio = y / THUMB_H
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            draw.line([(0, y), (THUMB_W, y)], fill=(r, g, b))
        return img

    def _compose(self, bg: Image.Image, title: str, variant: int) -> Image.Image:
        """Compose text over the background."""
        # Dark overlay for readability
        overlay = Image.new("RGBA", (THUMB_W, THUMB_H), (0, 0, 0, 140))
        bg = bg.convert("RGBA")
        bg.paste(overlay, (0, 0), overlay)
        bg = bg.convert("RGB")

        draw = ImageDraw.Draw(bg)

        # Try to load a bold font, fallback to default
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", FONT_SIZE_LARGE)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE_SMALL)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = font_large

        # Wrap title to 2 lines max
        lines = textwrap.wrap(title.upper(), width=20)[:2]
        y_start = THUMB_H // 2 - (len(lines) * (FONT_SIZE_LARGE + 10)) // 2

        for line in lines:
            # Shadow
            draw.text((62, y_start + 4), line, font=font_large, fill=(0, 0, 0, 180))
            # Main text
            draw.text((60, y_start), line, font=font_large, fill=(255, 255, 255))
            y_start += FONT_SIZE_LARGE + 12

        # Accent bar at bottom
        accent = (255, 80, 0) if variant == 0 else (0, 180, 255)
        draw.rectangle([(0, THUMB_H - 8), (THUMB_W, THUMB_H)], fill=accent)

        return bg

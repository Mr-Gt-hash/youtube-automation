"""
YouTube Automation Pipeline — Entry Point
Run the full pipeline: research → script → voiceover → thumbnail → video → upload
"""

import logging
import argparse
from pathlib import Path
from datetime import datetime

from config.settings import Settings
from src.niche_research.trends_scraper import TrendsScraper
from src.script_generator.gpt_writer import ScriptWriter
from src.voiceover.tts_engine import TTSEngine
from src.thumbnail.generator import ThumbnailGenerator
from src.video_editor.assembler import VideoAssembler
from src.uploader.seo_generator import SEOGenerator
from src.uploader.youtube_client import YouTubeUploader
from src.analytics.notifier import Notifier

# ── Logging setup ──────────────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
log_file = f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger("pipeline")


def run_pipeline(topic: str | None = None, dry_run: bool = False):
    """Execute the full YouTube automation pipeline."""
    cfg = Settings()
    notifier = Notifier(cfg)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"output/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("🚀 Starting YouTube Automation Pipeline")
    logger.info(f"Run ID: {run_id} | Dry run: {dry_run}")
    logger.info("=" * 60)

    try:
        # ── Step 1: Niche / Trend Research ─────────────────────────────────────
        logger.info("📊 Step 1/7 — Niche & Trend Research")
        if topic:
            selected_topic = topic
            logger.info(f"Using provided topic: {selected_topic}")
        else:
            scraper = TrendsScraper(cfg)
            trending = scraper.get_trending_topics(niche=cfg.TARGET_NICHE, limit=10)
            selected_topic = scraper.pick_best_topic(trending)
            logger.info(f"Selected topic: {selected_topic}")

        # ── Step 2: Script Generation ───────────────────────────────────────────
        logger.info("✍️  Step 2/7 — Script Generation")
        writer = ScriptWriter(cfg)
        script = writer.generate(topic=selected_topic)
        script_path = output_dir / "script.json"
        writer.save(script, script_path)
        logger.info(f"Script saved → {script_path}")

        # ── Step 3: Voiceover ───────────────────────────────────────────────────
        logger.info("🎙️  Step 3/7 — Voiceover Synthesis")
        tts = TTSEngine(cfg)
        audio_path = output_dir / "voiceover.mp3"
        tts.synthesize(text=script["narration"], output_path=audio_path)
        logger.info(f"Voiceover saved → {audio_path}")

        # ── Step 4: Thumbnail ───────────────────────────────────────────────────
        logger.info("🖼️  Step 4/7 — Thumbnail Generation")
        thumb_gen = ThumbnailGenerator(cfg)
        thumbnails = thumb_gen.generate_variants(
            title=script["title"],
            output_dir=output_dir,
            variants=2,
        )
        logger.info(f"Thumbnails saved → {thumbnails}")

        # ── Step 5: Video Assembly ──────────────────────────────────────────────
        logger.info("🎬 Step 5/7 — Video Assembly")
        assembler = VideoAssembler(cfg)
        video_path = output_dir / "final_video.mp4"
        assembler.assemble(
            script=script,
            audio_path=audio_path,
            output_path=video_path,
        )
        logger.info(f"Video assembled → {video_path}")

        # ── Step 6: SEO Metadata ────────────────────────────────────────────────
        logger.info("🏷️  Step 6/7 — SEO Metadata Generation")
        seo = SEOGenerator(cfg)
        metadata = seo.generate(script=script, topic=selected_topic)
        meta_path = output_dir / "metadata.json"
        seo.save(metadata, meta_path)
        logger.info(f"Metadata saved → {meta_path}")

        # ── Step 7: Upload ──────────────────────────────────────────────────────
        if dry_run:
            logger.info("🔵 Step 7/7 — DRY RUN: Skipping upload")
        else:
            logger.info("⬆️  Step 7/7 — Uploading to YouTube")
            uploader = YouTubeUploader(cfg)
            video_id = uploader.upload(
                video_path=video_path,
                thumbnail_path=thumbnails[0],
                metadata=metadata,
            )
            logger.info(f"✅ Video uploaded! ID: {video_id}")
            logger.info(f"🔗 https://youtu.be/{video_id}")
            notifier.send_success(video_id=video_id, title=metadata["title"])

        logger.info("🎉 Pipeline completed successfully!")
        return True

    except Exception as exc:
        logger.exception(f"Pipeline failed: {exc}")
        notifier.send_failure(error=str(exc))
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Automation Pipeline")
    parser.add_argument("--topic", type=str, help="Override topic (skip trend research)")
    parser.add_argument("--dry-run", action="store_true", help="Skip upload step")
    args = parser.parse_args()

    success = run_pipeline(topic=args.topic, dry_run=args.dry_run)
    raise SystemExit(0 if success else 1)

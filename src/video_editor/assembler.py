"""
Video Assembler — stitches B-roll, voiceover, captions and background music
into a final 1080p MP4 using MoviePy.
"""

import json
import logging
import requests
import random
from pathlib import Path
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
    concatenate_videoclips, CompositeAudioClip,
)
from moviepy.video.fx.all import fadein, fadeout

logger = logging.getLogger(__name__)

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"


class VideoAssembler:
    def __init__(self, cfg):
        self.cfg = cfg

    def assemble(self, script: dict, audio_path: Path, output_path: Path) -> Path:
        """Build the final video from components."""
        logger.info("Assembling video…")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Load voiceover
        voiceover = AudioFileClip(str(audio_path))
        total_duration = voiceover.duration

        # Fetch and assemble B-roll clips
        clips = self._get_broll_clips(
            topic=script.get("topic", "technology"),
            total_duration=total_duration,
        )

        if not clips:
            # Fallback: black background
            from moviepy.editor import ColorClip
            clips = [ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=total_duration)]

        # Concatenate clips to match audio length
        video = concatenate_videoclips(clips, method="compose")
        if video.duration < total_duration:
            video = video.loop(duration=total_duration)
        video = video.subclip(0, total_duration)

        # Mix voiceover with subtle background music
        audio = self._mix_audio(voiceover, total_duration)

        # Compose
        final = video.set_audio(audio)
        final = final.resize((1920, 1080))

        logger.info(f"Rendering video ({total_duration:.0f}s)…")
        final.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            threads=4,
            preset="fast",
            logger=None,
        )

        voiceover.close()
        final.close()
        logger.info(f"Video rendered → {output_path}")
        return output_path

    def _get_broll_clips(self, topic: str, total_duration: float) -> list:
        """Download B-roll clips from Pexels matching the topic."""
        clips = []
        try:
            headers = {"Authorization": self.cfg.PEXELS_API_KEY}
            r = requests.get(
                PEXELS_VIDEO_URL,
                headers=headers,
                params={"query": topic, "per_page": 10, "min_duration": 5, "max_duration": 30},
                timeout=10,
            )
            r.raise_for_status()
            videos = r.json().get("videos", [])
            random.shuffle(videos)

            tmp_dir = Path("output/tmp_broll")
            tmp_dir.mkdir(parents=True, exist_ok=True)

            accumulated = 0
            for vid in videos:
                if accumulated >= total_duration:
                    break
                file_url = next(
                    (f["link"] for f in vid.get("video_files", []) if f.get("quality") == "hd"),
                    None,
                )
                if not file_url:
                    continue
                tmp_path = tmp_dir / f"broll_{vid['id']}.mp4"
                if not tmp_path.exists():
                    resp = requests.get(file_url, timeout=30)
                    tmp_path.write_bytes(resp.content)
                clip = VideoFileClip(str(tmp_path)).without_audio()
                clips.append(clip)
                accumulated += clip.duration

        except Exception as e:
            logger.warning(f"B-roll fetch failed: {e}")

        return clips

    def _mix_audio(self, voiceover: AudioFileClip, duration: float) -> CompositeAudioClip:
        """Layer voiceover over quiet background music if available."""
        bgm_path = Path("assets/bgm.mp3")
        if bgm_path.exists():
            try:
                bgm = AudioFileClip(str(bgm_path)).volumex(0.08).audio_loop(duration=duration)
                return CompositeAudioClip([voiceover, bgm])
            except Exception:
                pass
        return voiceover

"""
Voiceover Engine — ElevenLabs primary, Google TTS fallback.
Applies audio normalisation and silence trimming.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self._engine = self._detect_engine()

    def _detect_engine(self) -> str:
        if self.cfg.ELEVENLABS_API_KEY and self.cfg.ELEVENLABS_VOICE_ID:
            logger.info("TTS engine: ElevenLabs")
            return "elevenlabs"
        logger.info("TTS engine: gTTS (fallback)")
        return "gtts"

    def synthesize(self, text: str, output_path: Path) -> Path:
        """Convert text to speech and save to output_path."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self._engine == "elevenlabs":
            self._elevenlabs(text, output_path)
        else:
            self._gtts(text, output_path)

        self._post_process(output_path)
        logger.info(f"Voiceover saved → {output_path}")
        return output_path

    def _elevenlabs(self, text: str, path: Path) -> None:
        from elevenlabs import generate, save
        audio = generate(
            text=text,
            voice=self.cfg.ELEVENLABS_VOICE_ID,
            model="eleven_multilingual_v2",
            api_key=self.cfg.ELEVENLABS_API_KEY,
        )
        save(audio, str(path))

    def _gtts(self, text: str, path: Path) -> None:
        from gtts import gTTS
        # gTTS has a char limit; chunk if needed
        chunks = [text[i:i+4900] for i in range(0, len(text), 4900)]
        if len(chunks) == 1:
            gTTS(text=text, lang=self.cfg.VIDEO_LANGUAGE, slow=False).save(str(path))
        else:
            from pydub import AudioSegment
            combined = AudioSegment.empty()
            for i, chunk in enumerate(chunks):
                tmp = path.parent / f"_chunk_{i}.mp3"
                gTTS(text=chunk, lang=self.cfg.VIDEO_LANGUAGE, slow=False).save(str(tmp))
                combined += AudioSegment.from_mp3(str(tmp))
                tmp.unlink()
            combined.export(str(path), format="mp3")

    def _post_process(self, path: Path) -> None:
        """Normalise audio levels and trim leading/trailing silence."""
        try:
            from pydub import AudioSegment, effects
            audio = AudioSegment.from_mp3(str(path))
            audio = effects.normalize(audio)
            # Trim silence > 1s at start/end
            audio = audio.strip_silence(silence_len=1000, silence_thresh=-40, padding=200)
            audio.export(str(path), format="mp3")
        except Exception as e:
            logger.warning(f"Post-processing skipped: {e}")

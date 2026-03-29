"""
Audio transcription utilities (faster-whisper).
"""
from pathlib import Path
from faster_whisper import WhisperModel


class Transcriber:
    def __init__(
        self,
        model_name: str = "base",
        language: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.language = language
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")

    def transcribe_audio(self, audio_path: Path):
        segments, info = self.model.transcribe(
            str(audio_path),
            language=self.language,
        )

        items = []
        for segment in segments:
            items.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                }
            )

        return {
            "language": self.language or info.language,
            "model": self.model_name,
            "segments": items,
        }


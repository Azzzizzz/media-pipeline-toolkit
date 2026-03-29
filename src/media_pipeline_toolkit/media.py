"""
Media inspection and extraction utilities (ffmpeg/ffprobe wrappers).
"""
import json
import subprocess
from pathlib import Path


def extract_audio(video_path: Path, audio_path: Path) -> None:
    """
    Extracts audio from a video file into a 16kHz mono WAV format using ffmpeg.
    """
    cmd = [
        "ffmpeg",
        "-y",               # Overwrite output files without asking
        "-i",
        str(video_path),
        "-vn",              # Disable video
        "-ac",
        "1",                # 1 audio channel (mono)
        "-ar",
        "16000",            # 16kHz sample rate for whisper
        str(audio_path),
    ]
    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )


def get_duration_seconds(path: Path) -> float:
    """
    Uses ffprobe to extract the exact media duration in seconds.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    return float(payload["format"]["duration"])


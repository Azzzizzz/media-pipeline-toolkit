"""
Orchestration for processing pipelines (e.g. video to transcript).
"""
import logging
import time
from pathlib import Path
from datetime import datetime

from media_pipeline_toolkit.media import extract_audio, get_duration_seconds
from media_pipeline_toolkit.chunking import split_audio_into_chunks, merge_chunk_results
from media_pipeline_toolkit.transcription import Transcriber
from media_pipeline_toolkit.formats import save_srt, save_vtt, save_txt, save_json
from media_pipeline_toolkit.manifest import write_manifest
from media_pipeline_toolkit.logging_utils import get_logger

logger = get_logger(__name__)


def process_audio_pipeline(
    audio_path: Path,
    output_dir: Path,
    model_name: str = "base",
    language: str | None = None,
    chunk_seconds: int = 900,
    formats: list[str] = None,
) -> dict:
    """
    Full pipeline for transcribing an audio file.
    """
    if formats is None:
        formats = ["txt", "srt", "vtt", "json"]

    output_dir.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now()
    
    # 1. Inspect
    duration = get_duration_seconds(audio_path)
    logger.info(f"Processing audio: {audio_path.name} ({duration:.2f}s)")

    # 2. Chunk if needed
    transcriber = Transcriber(model_name=model_name, language=language)
    
    if duration > chunk_seconds:
        logger.info(f"Duration exceeds {chunk_seconds}s. Splitting into chunks...")
        chunks_dir = output_dir / "chunks"
        chunks = split_audio_into_chunks(audio_path, chunks_dir, chunk_seconds=chunk_seconds)
        logger.info(f"Transcribing {len(chunks)} chunks...")
        segments = merge_chunk_results(chunks, transcriber)
    else:
        logger.info("Transcribing audio...")
        res = transcriber.transcribe_audio(audio_path)
        segments = res["segments"]
        language = res["language"]  # Update if detected

    # 3. Export
    output_files = {}
    if "txt" in formats:
        p = output_dir / "transcript.txt"
        save_txt(segments, p)
        output_files["txt"] = str(p)
    if "srt" in formats:
        p = output_dir / "transcript.srt"
        save_srt(segments, p)
        output_files["srt"] = str(p)
    if "vtt" in formats:
        p = output_dir / "transcript.vtt"
        save_vtt(segments, p)
        output_files["vtt"] = str(p)
    if "json" in formats:
        p = output_dir / "transcript.json"
        save_json({"segments": segments, "language": language, "model": model_name}, p)
        output_files["json"] = str(p)

    # 4. Manifest
    end_time = datetime.now()
    manifest = {
        "source_path": str(audio_path),
        "source_type": "audio",
        "duration_seconds": duration,
        "model_used": model_name,
        "language": language,
        "output_files": output_files,
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "status": "completed",
    }
    write_manifest(output_dir / "manifest.json", manifest)
    
    logger.info(f"Finished processing: {audio_path.name}")
    return manifest


def process_video_pipeline(
    video_path: Path,
    output_dir: Path,
    model_name: str = "base",
    language: str | None = None,
    chunk_seconds: int = 900,
    formats: list[str] = None,
) -> dict:
    """
    Full pipeline for transcribing a video file by extracting audio first.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / "audio.wav"
    
    logger.info(f"Extracting audio from {video_path.name}...")
    extract_audio(video_path, audio_path)
    
    manifest = process_audio_pipeline(
        audio_path=audio_path,
        output_dir=output_dir,
        model_name=model_name,
        language=language,
        chunk_seconds=chunk_seconds,
        formats=formats,
    )
    
    # Update manifest type
    manifest["source_path"] = str(video_path)
    manifest["source_type"] = "video"
    write_manifest(output_dir / "manifest.json", manifest)
    
    return manifest


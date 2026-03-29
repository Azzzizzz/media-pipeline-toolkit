"""
Batch processing utilities for entire directories.
"""
import json
import logging
from pathlib import Path
from media_pipeline_toolkit.pipeline import process_video_pipeline, process_audio_pipeline
from media_pipeline_toolkit.logging_utils import get_logger

logger = get_logger(__name__)

SUPPORTED_VIDEO = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
SUPPORTED_AUDIO = {".wav", ".mp3", ".m4a", ".flac"}


def is_already_completed(output_dir: Path) -> bool:
    """
    Checks if a manifest.json exists in the output dir and has status 'completed'.
    """
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        return False
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data.get("status") == "completed"
    except Exception:
        return False


def process_directory(
    input_dir: Path,
    output_dir: Path,
    model_name: str = "base",
    language: str | None = None,
    chunk_seconds: int = 900,
    formats: list[str] = None,
    resume: bool = False,
):
    """
    Scans input_dir for media files and processes them one by one.
    """
    if not input_dir.is_dir():
        logger.error(f"Input directory does not exist: {input_dir}")
        return

    files = [f for f in input_dir.iterdir() if f.is_file()]
    logger.info(f"Found {len(files)} files in {input_dir}")

    for f in files:
        ext = f.suffix.lower()
        is_video = ext in SUPPORTED_VIDEO
        is_audio = ext in SUPPORTED_AUDIO
        
        if not (is_video or is_audio):
            logger.debug(f"Skipping unsupported file: {f.name}")
            continue

        # Create a specific output subfolder for this file
        job_output_dir = output_dir / f.stem
        
        if resume and is_already_completed(job_output_dir):
            logger.info(f"Skipping already completed file: {f.name}")
            continue

        logger.info(f"Processing candidate: {f.name}")
        try:
            if is_video:
                process_video_pipeline(
                    video_path=f,
                    output_dir=job_output_dir,
                    model_name=model_name,
                    language=language,
                    chunk_seconds=chunk_seconds,
                    formats=formats,
                )
            else:
                process_audio_pipeline(
                    audio_path=f,
                    output_dir=job_output_dir,
                    model_name=model_name,
                    language=language,
                    chunk_seconds=chunk_seconds,
                    formats=formats,
                )
        except Exception as e:
            logger.error(f"Failed to process {f.name}: {e}", exc_info=True)


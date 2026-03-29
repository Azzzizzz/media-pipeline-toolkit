"""
Chunking logic for long audio files.
"""
import subprocess
from pathlib import Path
from media_pipeline_toolkit.media import get_duration_seconds


def split_audio_into_chunks(
    audio_path: Path,
    output_dir: Path,
    chunk_seconds: int = 900,
) -> list[tuple[Path, float]]:
    """
    Splits a large audio file into smaller segments using ffmpeg.
    Returns a list of (chunk_path, offset_seconds).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    chunk_pattern = output_dir / "chunk_%03d.wav"
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(audio_path),
        "-f", "segment",
        "-segment_time", str(chunk_seconds),
        "-c", "copy",
        str(chunk_pattern),
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    chunk_files = sorted(output_dir.glob("chunk_*.wav"))
    chunks_with_offsets = []
    current_offset = 0.0
    
    for chunk in chunk_files:
        chunks_with_offsets.append((chunk, current_offset))
        # Measure actual duration to avoid drift
        current_offset += get_duration_seconds(chunk)
        
    return chunks_with_offsets


def merge_chunk_results(
    chunks_with_offsets: list[tuple[Path, float]],
    transcriber,
) -> list[dict]:
    """
    Transcribes chunks one by one and merges results with timestamp offsets.
    """
    merged_segments = []
    
    for chunk_path, offset in chunks_with_offsets:
        result = transcriber.transcribe_audio(chunk_path)
        for segment in result["segments"]:
            merged_segments.append({
                "start": segment["start"] + offset,
                "end": segment["end"] + offset,
                "text": segment["text"],
            })
            
    return merged_segments


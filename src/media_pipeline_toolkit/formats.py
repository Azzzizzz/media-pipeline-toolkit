"""
Output struct formatting (SRT, VTT, TXT, JSON).
"""
import json
from pathlib import Path


def format_srt_timestamp(seconds: float) -> str:
    total_ms = int(seconds * 1000)
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    secs = (total_ms % 60_000) // 1000
    millis = total_ms % 1000
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def format_vtt_timestamp(seconds: float) -> str:
    total_ms = int(seconds * 1000)
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    secs = (total_ms % 60_000) // 1000
    millis = total_ms % 1000
    return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"


def save_srt(segments: list[dict], output_path: Path) -> None:
    rows = []
    for index, segment in enumerate(segments, start=1):
        rows.append(str(index))
        rows.append(
            f"{format_srt_timestamp(segment['start'])} --> "
            f"{format_srt_timestamp(segment['end'])}"
        )
        rows.append(segment["text"])
        rows.append("")
        
    output_path.write_text("\n".join(rows), encoding="utf-8")


def save_vtt(segments: list[dict], output_path: Path) -> None:
    rows = ["WEBVTT", ""]
    for segment in segments:
        rows.append(
            f"{format_vtt_timestamp(segment['start'])} --> "
            f"{format_vtt_timestamp(segment['end'])}"
        )
        rows.append(segment["text"])
        rows.append("")
        
    output_path.write_text("\n".join(rows), encoding="utf-8")


def save_txt(segments: list[dict], output_path: Path) -> None:
    rows = [segment["text"] for segment in segments]
    output_path.write_text("\n".join(rows), encoding="utf-8")


def save_json(payload: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


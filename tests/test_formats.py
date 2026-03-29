import json
import pytest
from pathlib import Path
from media_pipeline_toolkit.formats import (
    format_srt_timestamp,
    format_vtt_timestamp,
    save_srt,
    save_vtt,
    save_txt,
    save_json,
)


def test_format_srt_timestamp():
    # 1 hour = 3600, 1 minute = 60, 2 seconds, 450 ms
    val = format_srt_timestamp(3662.450)
    assert val == "01:01:02,450"


def test_format_vtt_timestamp():
    val = format_vtt_timestamp(3662.450)
    assert val == "01:01:02.450"


def test_save_srt(tmp_path: Path):
    segments = [
        {"start": 0.0, "end": 1.5, "text": "Hello."},
        {"start": 1.5, "end": 3.0, "text": "World."},
    ]
    f = tmp_path / "test.srt"
    save_srt(segments, f)
    
    content = f.read_text(encoding="utf-8")
    assert "1\n00:00:00,000 --> 00:00:01,500\nHello." in content
    assert "2\n00:00:01,500 --> 00:00:03,000\nWorld." in content


def test_save_vtt(tmp_path: Path):
    segments = [{"start": 0.5, "end": 2.25, "text": "Subtitle."}]
    f = tmp_path / "test.vtt"
    save_vtt(segments, f)
    
    content = f.read_text(encoding="utf-8")
    assert content.startswith("WEBVTT\n\n")
    assert "00:00:00.500 --> 00:00:02.250\nSubtitle." in content


def test_save_txt(tmp_path: Path):
    segments = [
        {"start": 0.0, "end": 1.0, "text": "Line 1"},
        {"start": 1.0, "end": 2.0, "text": "Line 2"},
    ]
    f = tmp_path / "test.txt"
    save_txt(segments, f)
    
    assert f.read_text(encoding="utf-8") == "Line 1\nLine 2"


def test_save_json(tmp_path: Path):
    payload = {"status": "ok", "duration": 5.0}
    f = tmp_path / "test.json"
    save_json(payload, f)
    
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["duration"] == 5.0

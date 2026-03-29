"""
Data models for the application using pydantic.
"""
from pathlib import Path
from pydantic import BaseModel

class OutputPaths(BaseModel):
    audio: Path | None = None
    txt: Path | None = None
    srt: Path | None = None
    vtt: Path | None = None
    json: Path | None = None

"""
Manifest generation and parsing.
"""
import json
from pathlib import Path


def write_manifest(output_path: Path, payload: dict) -> None:
    """
    Writes a machine-readable JSON manifest for the job.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


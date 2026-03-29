# Media Pipeline Toolkit

## 1. Project Summary

**Project name:** `media-pipeline-toolkit`

**One-line idea:**  
An open-source Python CLI for processing video and audio files, extracting audio, generating transcripts, exporting multiple subtitle formats, and handling long-running batch workflows with production-grade metadata and manifests.

**Why this name works better:**  
It is not limited to courses. It is not limited to transcripts. It leaves room for future media-processing features while keeping the first release focused and practical.

## 2. Product Goals

This project should support these use cases:

1. Take a video and produce an audio file.
2. Take an audio file and produce a transcript.
3. Take a video and produce a transcript directly.
4. Export transcripts as `.txt`, `.srt`, `.vtt`, and `.json`.
5. Chunk long media files automatically.
6. Support production-grade structure and reliability.
7. Process files in batch mode.
8. Write a metadata manifest with duration, source file, model used, and output paths.

## 3. Project Vision

The first public version should feel like a real CLI tool, not a one-off script.

That means:

- clear commands
- consistent output folders
- error handling
- manifest files
- logs
- idempotent processing where possible
- clean module boundaries
- one canonical entrypoint

## 4. Recommended Scope for v0.1.0

Keep the first release focused, but not too small.

### Version `0.1.0` should include

- `video -> audio`
- `audio -> transcript`
- `video -> transcript`
- output formats:
  - `.txt`
  - `.srt`
  - `.vtt`
  - `.json`
- automatic chunking for long files
- batch mode for folders
- manifest generation

### Version `0.1.0` should not include yet

- speaker diarization
- translation
- OCR from frames
- web UI
- cloud job queue

Those can come later.

## 5. Suggested Repository Structure

```text
media-pipeline-toolkit/
├── PROJECT_PLAN.md
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── src/
│   └── media_pipeline_toolkit/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_utils.py
│       ├── models.py
│       ├── media.py
│       ├── chunking.py
│       ├── transcription.py
│       ├── formats.py
│       ├── manifest.py
│       ├── pipeline.py
│       └── batch.py
├── examples/
│   └── sample_commands.md
├── scripts/
│   └── run_local.sh
└── tests/
    ├── test_media.py
    ├── test_chunking.py
    ├── test_formats.py
    ├── test_manifest.py
    └── test_pipeline.py
```

## 6. Core Features

### Feature 1: Video to audio

Input:

- `.mp4`
- `.mov`
- `.mkv`

Output:

- `.wav` by default
- optional `.mp3`

### Feature 2: Audio to transcript

Input:

- `.wav`
- `.mp3`
- `.m4a`

Output:

- structured transcript with timestamps

### Feature 3: Video to transcript

Pipeline:

1. extract audio
2. chunk if needed
3. transcribe
4. merge transcript segments
5. export outputs

### Feature 4: Multi-format transcript export

Supported export formats:

- `.txt`
- `.srt`
- `.vtt`
- `.json`

### Feature 5: Long-file chunking

Use chunking to make long files safer and easier to process.

Approach:

- inspect media duration
- if duration exceeds threshold, split audio into chunks
- transcribe chunk by chunk
- offset timestamps when merging results

### Feature 6: Batch mode

Batch mode should:

- scan a folder
- detect supported files
- process one by one
- skip outputs that already exist if `--resume` is used
- write a per-file manifest

#### Resume detection

When `--resume` is used, a file is considered already processed only if its output directory contains a `manifest.json` with:

- `"status": "completed"`
- matching `source_path`
- matching source identity fields such as:
  - file size
  - last modified timestamp
  - optional checksum

Any other state should be treated as incomplete and reprocessed:

- missing manifest
- `"status": "failed"`
- partial outputs
- changed source file metadata

### Feature 7: Metadata manifest

Each processed file should have a machine-readable manifest.

Example fields:

- source path
- source type
- source size bytes
- source modified time
- optional source checksum
- duration
- chunk count
- model name
- language
- output files
- started at
- completed at
- processing status

## 7. Recommended Technology Choices

### Core stack

- `Python 3.11+`
- `ffmpeg`
- `ffprobe`
- `faster-whisper`
- `argparse`
- `pathlib`
- `PyYAML`
- `pydantic` for clean models and validation

### Why these tools

- `ffmpeg` is the standard tool for media processing.
- `ffprobe` is reliable for duration and metadata inspection.
- `faster-whisper` gives local transcription, timestamps, and solid performance.
- `argparse` keeps the CLI simple for a beginner-friendly open-source project.
- `PyYAML` enables reusable job configs for repeatable runs.
- `pydantic` helps keep manifests and internal data models clean.

## 8. Production-Grade Requirements

If you want this to feel production grade, design for these from the start:

- structured error handling
- deterministic output paths
- reusable modules
- typed functions
- manifest files
- logging
- resumable processing
- source-change detection for safe resume
- tests for formatters and pipelines
- clean CLI help output

### Production-grade does not mean overengineered

It should still be:

- understandable
- easy to run locally
- easy to contribute to

## 9. CLI Design

These commands are a good shape for the tool.

### Approach 1: Direct CLI flags

This should be the default approach in the documentation because it is the easiest for beginners.

### Extract audio

```bash
python -m media_pipeline_toolkit extract-audio \
  --input "video.mp4" \
  --output "outputs/video/audio.wav"
```

### Transcribe audio

```bash
python -m media_pipeline_toolkit transcribe-audio \
  --input "audio.wav" \
  --output-dir "outputs/audio-job" \
  --model "base" \
  --language "en" \
  --chunk-seconds 900 \
  --formats txt srt vtt json
```

### Transcribe video directly

```bash
python -m media_pipeline_toolkit transcribe-video \
  --input "video.mp4" \
  --output-dir "outputs/video-job" \
  --model "base" \
  --language "en" \
  --chunk-seconds 900 \
  --formats txt srt vtt json
```

### Batch mode

```bash
python -m media_pipeline_toolkit batch \
  --input-dir "videos" \
  --output-dir "outputs/batch-run" \
  --model "base" \
  --language "en" \
  --chunk-seconds 900 \
  --formats txt srt vtt json \
  --resume
```

### Approach 2: Config file mode

This is the better approach for repeatable jobs, GitHub examples, and production-style usage.

```bash
python -m media_pipeline_toolkit run --config job.yaml
```

Example `job.yaml`:

```yaml
job_type: transcribe-video
input: "video.mp4"
output_dir: "outputs/video-job"
formats:
  - txt
  - srt
  - vtt
  - json
chunking:
  enabled: true
  chunk_seconds: 900
transcription:
  model: "base"
  language: "en"
```

### Approach 3: Smart default output paths

If the user does not provide `--output` or `--output-dir`, the tool should create predictable defaults automatically.

Example:

```bash
python -m media_pipeline_toolkit transcribe-video \
  --input "video.mp4"
```

Expected default output path:

```text
outputs/video/
```

For a source file named `my-lesson.mp4`, the tool could create:

```text
outputs/my-lesson/
```

and place all generated files there.

### Config precedence rules

The precedence should be explicit:

1. CLI flags
2. config file values
3. built-in defaults

Example:

- if `job.yaml` defines `formats: [txt, srt]`
- and the CLI passes `--formats txt json`
- then the final formats should be `txt json`

This same rule should apply to:

- formats
- language
- chunk size
- model selection
- output paths

### Collision behavior

If the target output folder already exists, the tool should not overwrite silently by default.

Recommended behavior:

- default: fail with a clear error
- `--resume`: reuse existing outputs and skip completed work
- `--overwrite`: replace generated outputs for the current job

This should apply to both explicit output paths and smart default output paths.

### Recommendation

The project should support all three approaches:

1. direct CLI flags for simple runs
2. config file mode for repeatable and shareable jobs
3. smart default output paths when output is omitted

This gives the project a clean beginner path and a stronger production path without making the interface confusing.

### Canonical entrypoint

The canonical way to run the tool should be:

```bash
python -m media_pipeline_toolkit ...
```

This is why `__main__.py` is included in the package structure. It gives the project one stable public entrypoint and avoids teaching users to call internal modules like `cli.py` directly.

## 10. Example Output Structure

```text
outputs/
└── section-05/
    ├── audio.wav
    ├── transcript.txt
    ├── transcript.srt
    ├── transcript.vtt
    ├── transcript.json
    └── manifest.json
```

## 11. Setup Commands

### Create project folder

```bash
mkdir media-pipeline-toolkit
cd media-pipeline-toolkit
```

### Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Install dependencies

```bash
pip install faster-whisper pydantic pyyaml
```

### Install the local package

Because the project uses a `src/` layout, install it in editable mode before running commands:

```bash
pip install -e .
```

### Optional development dependencies

```bash
pip install pytest ruff mypy
```

### Check system tools

```bash
ffmpeg -version
ffprobe -version
```

### Run the CLI

```bash
python -m media_pipeline_toolkit --help
```

## 12. Example `requirements.txt`

```txt
faster-whisper
pydantic
PyYAML
```

## 13. Example `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
.DS_Store
outputs/
.pytest_cache/
.mypy_cache/
```

## 14. Module Responsibilities

### `media.py`

Responsible for:

- validating input files
- extracting audio
- probing media duration and metadata

### `chunking.py`

Responsible for:

- deciding when to chunk
- splitting long audio files
- computing timestamp offsets

### `transcription.py`

Responsible for:

- model loading
- audio transcription
- merging transcript chunks

### `formats.py`

Responsible for:

- writing `.txt`
- writing `.srt`
- writing `.vtt`
- writing `.json`

### `manifest.py`

Responsible for:

- building structured metadata
- saving `manifest.json`

### `pipeline.py`

Responsible for:

- video to audio flow
- audio to transcript flow
- video to transcript flow

### `batch.py`

Responsible for:

- walking directories
- filtering supported inputs
- running pipeline jobs in sequence

### `cli.py`

Responsible for:

- parsing commands
- calling the correct pipeline
- printing useful status messages

### `config.py`

Responsible for:

- reading YAML job files
- validating config defaults
- merging CLI flags with config values
- applying precedence rules: CLI > config > defaults

### `logging_utils.py`

Responsible for:

- configuring console logging
- choosing log levels
- formatting progress and error messages
- optionally writing log files for batch runs

### `models.py`

Responsible for:

- defining typed data models
- validating transcript segments and manifest payloads
- keeping internal data structures consistent across modules

## 15. Data Models to Use

Use simple structured models instead of loose dictionaries everywhere.

Suggested models:

- `MediaInfo`
- `TranscriptSegment`
- `TranscriptResult`
- `OutputPaths`
- `ManifestRecord`

Example:

```python
from pathlib import Path
from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class OutputPaths(BaseModel):
    audio: Path | None = None
    txt: Path | None = None
    srt: Path | None = None
    vtt: Path | None = None
    json: Path | None = None
```

## 16. First Code Snippet: Extract Audio from Video

```python
from pathlib import Path
import subprocess


def extract_audio(video_path: Path, audio_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(audio_path),
    ]
    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )
```

## 17. Second Code Snippet: Read Media Duration

```python
from pathlib import Path
import json
import subprocess


def get_duration_seconds(path: Path) -> float:
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
```

## 18. Third Code Snippet: Transcribe Audio

```python
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
```

### Why this structure matters

The model should be loaded once and reused across files, especially in batch mode. Loading it inside every function call would slow the project down unnecessarily. Passing `language` here also keeps the CLI, YAML config, and transcription layer aligned.

## 19. Fourth Code Snippet: Chunk Long Audio

This is one practical chunking strategy.

```python
from pathlib import Path
import subprocess


def split_audio_into_chunks(
    audio_path: Path,
    output_dir: Path,
    chunk_seconds: int = 900,
) -> list[tuple[Path, float]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    chunk_pattern = output_dir / "chunk_%03d.wav"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(audio_path),
        "-f",
        "segment",
        "-segment_time",
        str(chunk_seconds),
        "-c",
        "copy",
        str(chunk_pattern),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    chunk_files = sorted(output_dir.glob("chunk_*.wav"))
    chunks_with_offsets = []
    offset_seconds = 0.0

    for chunk in chunk_files:
        chunks_with_offsets.append((chunk, offset_seconds))
        offset_seconds += get_duration_seconds(chunk)

    return chunks_with_offsets
```

### Chunking note

The return value is a list of `(chunk_path, offset_seconds)` pairs. For production correctness, offsets should come from measured chunk durations or segment start times, not from `index * chunk_seconds`, because real chunk boundaries may drift slightly.

## 20. Fifth Code Snippet: Merge Chunked Transcript Segments with Timestamp Offsets

```python
from pathlib import Path


def merge_chunk_results(
    chunks: list[tuple[Path, float]],
    transcriber: "Transcriber",
) -> list[dict]:
    merged = []
    for chunk_path, offset_seconds in chunks:
        result = transcriber.transcribe_audio(chunk_path)
        for segment in result["segments"]:
            merged.append(
                {
                    "start": segment["start"] + offset_seconds,
                    "end": segment["end"] + offset_seconds,
                    "text": segment["text"],
                }
            )
    return merged
```

This connects directly to `split_audio_into_chunks`. The full chunking flow looks like:

```python
chunks = split_audio_into_chunks(audio_path, chunks_dir, chunk_seconds=900)
segments = merge_chunk_results(chunks, transcriber)
```

Example with two chunks:

- chunk_000.wav has offset `0` → segment at `0.5s` stays at `0.5s`
- chunk_001.wav has offset `900` → segment at `1.0s` becomes `901.0s`

Merged result:

```python
[
    {"start": 0.5, "end": 3.2, "text": "Hello everyone."},
    {"start": 901.0, "end": 904.4, "text": "Welcome back."},
]
```

This is the key step that makes chunking safe while keeping final subtitle timestamps correct.

## 21. Sixth Code Snippet: Save SRT

```python
from pathlib import Path


def format_srt_timestamp(seconds: float) -> str:
    total_ms = int(seconds * 1000)
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    secs = (total_ms % 60_000) // 1000
    millis = total_ms % 1000
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


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
```

## 22. Seventh Code Snippet: Save VTT

VTT is similar to SRT but has three differences: a `WEBVTT` header, `.` as the millisecond separator (not `,`), and no sequence numbers.

```python
from pathlib import Path


def format_vtt_timestamp(seconds: float) -> str:
    total_ms = int(seconds * 1000)
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    secs = (total_ms % 60_000) // 1000
    millis = total_ms % 1000
    return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"


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
```

## 23. Eighth Code Snippet: Save Manifest

```python
from pathlib import Path
import json


def write_manifest(output_path: Path, payload: dict) -> None:
    output_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
```

Example manifest:

```json
{
  "source_path": "video.mp4",
  "source_type": "video",
  "source_size_bytes": 184392112,
  "source_modified_time": "2026-03-29T10:15:30Z",
  "source_checksum_sha256": "optional-hash-value",
  "duration_seconds": 3521.73,
  "model_used": "base",
  "language": "en",
  "chunk_count": 4,
  "outputs": {
    "audio": "outputs/job/audio.wav",
    "txt": "outputs/job/transcript.txt",
    "srt": "outputs/job/transcript.srt",
    "vtt": "outputs/job/transcript.vtt",
    "json": "outputs/job/transcript.json"
  },
  "status": "completed"
}
```

## 24. Suggested CLI Flow

### `extract-audio`

Input:

- one video file

Output:

- one audio file

### `transcribe-audio`

Input:

- one audio file

Output:

- transcript files plus manifest

### `transcribe-video`

Input:

- one video file

Output:

- audio file
- transcript files
- manifest

### `batch`

Input:

- one folder

Output:

- one output subfolder per source file

### `run --config`

Input:

- one YAML config file

Output:

- the same outputs as the selected job type
- useful for reproducible runs and documented examples

## 25. Processing Strategy

For reliability, use this order:

1. validate source file
2. inspect media metadata
3. extract audio if source is video
4. chunk if file is too long
5. transcribe chunks
6. merge and offset timestamps
7. export requested formats
8. write manifest
9. print final summary

## 26. Roadmap

### Phase 1: Project foundation

- create repository structure
- add CLI skeleton
- add dependency management

### Phase 2: Media support

- add video to audio flow
- add media probing

### Phase 3: Transcription

- add audio transcription
- add video transcription

### Phase 4: Exports

- add `.txt`
- add `.srt`
- add `.vtt`
- add `.json`

### Phase 5: Chunking and manifests

- add chunk splitting
- add merged timestamp offsets
- add manifest output

### Phase 6: Batch mode and polish

- add folder processing
- add resume support
- improve logging
- add tests

## 27. Learning Path for You

Since you are new to Python, build it in this order:

1. `Path` from `pathlib`
2. `subprocess.run(...)`
3. simple functions
4. `argparse`
5. structured models
6. splitting logic into modules

You do not need to learn everything at once.

The best learning path is:

1. get `extract_audio()` working
2. get `transcribe_audio()` working
3. wire them together for `transcribe-video`
4. add `.txt`
5. add `.srt`
6. add `.vtt` and `.json`
7. add chunking
8. add batch mode
9. add manifests

## 28. Suggested README Positioning

You can later use this wording:

```md
# Media Pipeline Toolkit

An open-source Python CLI for extracting audio from video, generating transcripts
from audio or video, exporting subtitle formats, and processing media files in batch.
```

## 29. Final Recommendation

Use `media-pipeline-toolkit` as the repository name.

It is broad enough for GitHub, accurate for the current feature set, and still leaves room for future media-processing additions.

The best next step is to scaffold the real project files under:

```text
media-pipeline-toolkit/
```

and build these commands first:

1. `extract-audio`
2. `transcribe-audio`
3. `transcribe-video`
4. `batch`

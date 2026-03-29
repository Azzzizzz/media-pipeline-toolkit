# Media Pipeline Toolkit 🎬🔊

An open-source Python CLI for processing video and audio files. Extract audio, generate high-accuracy transcripts using AI, and export production-ready subtitle formats in batch.

---

## 🌟 What is this?

**Media Pipeline Toolkit** is a powerful, beginner-friendly tool designed to automate the tedious parts of media processing. Whether you have a single video or a folder with hundreds of lessons, this toolkit can "listen" to them and turn the speech into perfectly timed text.

It is built for developers who want a reliable, local, and private way to generate transcripts without sending data to expensive cloud services.

## ✨ Key Features

- **Video to Audio**: Extract high-quality WAV audio from any video format (`.mp4`, `.mov`, `.mkv`).
- **AI Transcription**: Uses the state-of-the-art **Faster-Whisper** engine for near-human accuracy.
- **Smart Chunking**: Automatically splits long videos (e.g., 2-hour lectures) into smaller segments to ensure the AI stays accurate and never "hallucinates."
- **Export Formats**: Generate `.srt`, `.vtt`, `.txt`, and `.json` files instantly.
- **Batch Processing**: Point it at a folder and go for coffee—the tool will process everything while you wait.
- **Resume Support**: Interrupted? No problem. The tool uses `manifest.json` files to remember what it finished and skips completed files when you restart.
- **Configuration Mode**: Control everything via a simple `job.yaml` file for repeatable workflows.

---

## ⚙️ Tech Stack & Why

- **Python 3.11+**: The industry standard for AI and media scripting.
- **Faster-Whisper**: A heavily optimized version of OpenAI's Whisper model that runs 4x faster on your local CPU.
- **FFmpeg & FFprobe**: The "gold standard" open-source tools for media manipulation.
- **Pydantic**: Ensures all data (transcripts, manifests) follows a strict, error-free structure.
- **PyYAML**: Allows for clean, human-readable configuration files.

---

## 🛠️ Installation

### 1. System Requirements

You **must** have `ffmpeg` and `ffprobe` installed on your system.

- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Setup

```bash
# Clone the repo and enter it
cd media-pipeline-toolkit

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

---

## 🚀 How to Use

### 1. Basic: Transcribe a Single Video

This is the easiest way to start. It extracts audio, transcribes, and saves all 4 formats.

```bash
python -m media_pipeline_toolkit transcribe-video --input "my_video.mp4"
```

### 2. Pro: Batch Process a Folder

Point to a folder of videos. Use `--resume` to skip files you've already finished.

```bash
python -m media_pipeline_toolkit batch --input-dir "my_videos/" --output-dir "outputs/" --resume
```

### 3. Expert: Use a Config File

Create a `job.yaml`:

```yaml
job_type: batch
input_dir: "course_videos/"
output_dir: "course_outputs/"
model: base
language: en
resume: true
```

Then run it:

```bash
python -m media_pipeline_toolkit run --config job.yaml
```

---

## 🧠 Choosing the Right Whisper Model

The toolkit supports multiple versions of the Whisper model. Larger models are more accurate but take significantly more time and memory to run.

| Model Name | RAM (int8) | Speed | Accuracy | Best For... |
| :--- | :--- | :--- | :--- | :--- |
| **tiny** | ~150 MB | 32x | Base | Super-fast testing / CPU-only |
| **base** | ~250 MB | 16x | Good | Standard English transcription |
| **small** | ~600 MB | 6x | Great | Multiple languages / Accents |
| **medium** | ~1.5 GB | 2x | Excellent | Near-human accuracy |
| **large-v3** | ~3.0 GB | 1x | Ultimate | Maximum precision / State-of-the-Art |

> [!TIP]
> For most English-based tutorials and courses, the **`base`** or **`small`** models provide the best balance between speed and quality.

---

## 📈 Performance Benchmarks

To give you an idea of how fast the tool is, here are some typical benchmarks running on a modern CPU (e.g., Apple M1/M2 or a mid-range Intel i7).

| Media Duration | Extraction (ffmpeg) | Transcription (tiny model) | Transcription (base model) |
| :--- | :--- | :--- | :--- |
| **1 Minute** | ~1 second | ~10 seconds | ~45 seconds |
| **5 Minutes** | ~2 seconds | ~45 seconds | ~3 minutes |
| **10 Minutes** | ~4 seconds | ~1.5 minutes | ~6 minutes |
| **60 Minutes** | ~15 seconds | ~8 minutes | ~35 minutes |

*Note: Transcription speed varies depending on your hardware and the Whisper model size you choose.*

---

## 🔄 The Pipeline Flow

When you run a `transcribe-video` command, here is exactly what happens under the hood:

### 1. Audio Extraction (The "Rip" Phase)

The tool uses **FFmpeg** to isolate the spoken track. It doesn't just copy the audio; it optimizes it specifically for AI processing:

- **Command**: `ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 audio.wav`
- **`-vn`**: Strips out all video data to save memory and speed.
- **`-ac 1`**: Converts audio to **Mono** (one channel). Whisper models are trained on mono data and don't need stereo.
- **`-ar 16000`**: Resamples the audio to **16kHz**. This is the native frequency Whisper expects; any higher is wasted processing power.

### 2. Intelligent Chunking

If the video is long (e.g., > 15 mins), it's sliced into segments.

- **Drift Prevention**: We use `ffprobe` to measure the *actual* millisecond length of every chunk to ensure subtitles never drift out of sync over time.

### 3. AI Transcription (The "Brain" Phase)

The tool loads the **Faster-Whisper** engine into your local RAM.

- **Technology**: It uses **CTranslate2**, a fast inference engine for Transformer models.
- **Quantization**: We use `int8` (8-bit) math. This allows the master AI model to run on a normal laptop without needing a massive $1,000 graphics card, while maintaining 99% of the accuracy.
- **Memory Management**: The model is loaded **once** at the start of a batch and reused for every file, making it much faster than one-off scripts.

### 4. Merging & Export

- The tool mathematically connects all transcript chunks, correcting the timestamps.
- Your `.srt`, `.vtt`, `.txt`, and `.json` files are written to the output folder.
- A `manifest.json` is saved to lock in the job's success.

---

## 📁 Output Structure

For every file processed, the tool creates a dedicated folder:

```text
outputs/
└── my_lesson/
    ├── audio.wav        # Extracted audio
    ├── transcript.txt   # Plain text
    ├── transcript.srt   # Subtitles (VLC/YouTube)
    ├── transcript.vtt   # Web Subtitles (HTML5)
    ├── transcript.json  # Raw data for developers
    └── manifest.json    # Job metadata & status
```

---

## 🧪 Running Tests

We take reliability seriously. Run the test suite with:

```bash
pytest
```

---

## 📜 License

MIT

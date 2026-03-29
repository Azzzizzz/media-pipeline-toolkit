# 🚀 Future Features Roadmap

This document outlines the recommended features for the next major versions of **Media Pipeline Toolkit**. Each feature is researched, compared with available open-source options, and ranked by implementation complexity.

---

## Feature 1: Real-Time Streaming Transcription 🎙️

### What Is It?

Instead of waiting for a file to be saved and then processing it, the tool would **listen to live audio** (from a microphone or audio stream) and display the transcript **as the person speaks**, like live captions on YouTube or Zoom.

### How Would It Work?

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Microphone   │────▶│  Audio Buffer │────▶│  Whisper AI   │────▶ Live Text
│  / Stream     │     │  (2-3s chunks)│     │  (tiny/base)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

1. A library like `sounddevice` or `pyaudio` captures raw audio from the microphone in real-time.
2. The audio is buffered into small windows (2-3 seconds each).
3. Each window is fed into the Whisper model for instant transcription.
4. The text is printed to the terminal (or pushed to a WebSocket for a web UI).

### Tech Options

| Library | Role | Why? |
| :--- | :--- | :--- |
| **sounddevice** | Mic capture | Simple Python API, cross-platform, no compilation needed |
| **pyaudio** | Mic capture | More mature but requires PortAudio system dependency |
| **faster-whisper** | Transcription | Already in our stack; supports streaming segments natively |
| **Parakeet TDT** | Alternative | Ultra-low latency model built specifically for real-time streaming |

### CLI Example (Proposed)

```bash
# Start live captioning from your microphone
python -m media_pipeline_toolkit live --model tiny

# Save the live session to a file when done
python -m media_pipeline_toolkit live --model base --output session.txt
```

### Complexity

| Aspect | Rating |
| :--- | :--- |
| **Difficulty** | ⭐⭐⭐ Medium |
| **New Dependencies** | `sounddevice` (lightweight) |
| **Estimated Time** | 2-3 days |

---

## Feature 2: Multi-Language Audio Track Support 🌍

### What Is It?

Many professional video files (`.mkv`, `.mp4`) contain **multiple audio tracks** in different languages. For example, a Netflix download might have Track 1 (English), Track 2 (Spanish), Track 3 (Japanese). This feature would let the user select which tracks to transcribe — or transcribe **all of them** automatically into separate subtitle files.

### How Would It Work?

```text
┌─────────────────┐
│   input.mkv      │
│                   │
│  Track 0: English │──▶ transcript_en.srt
│  Track 1: Spanish │──▶ transcript_es.srt
│  Track 2: Japanese│──▶ transcript_ja.srt
└─────────────────┘
```

1. `ffprobe` scans the video and lists all available audio streams with their language metadata.
2. The user selects specific tracks (`--tracks 0,2`) or uses `--all-tracks`.
3. Each selected track is extracted as a separate `.wav` file.
4. Each `.wav` is transcribed independently using the appropriate Whisper language setting.
5. Separate subtitle files are generated per track.

### FFmpeg Commands Involved

```bash
# Probe all tracks
ffprobe -v quiet -print_format json -show_streams input.mkv

# Extract specific track (e.g., track index 1)
ffmpeg -i input.mkv -map 0:a:1 -vn -ac 1 -ar 16000 track_1.wav
```

### CLI Example (Proposed)

```bash
# List available audio tracks
python -m media_pipeline_toolkit probe --input movie.mkv

# Transcribe specific tracks
python -m media_pipeline_toolkit transcribe-video --input movie.mkv --tracks 0,2

# Transcribe all tracks automatically
python -m media_pipeline_toolkit transcribe-video --input movie.mkv --all-tracks
```

### Complexity

| Aspect | Rating |
| :--- | :--- |
| **Difficulty** | ⭐⭐ Low-Medium |
| **New Dependencies** | None (already using ffmpeg + ffprobe) |
| **Estimated Time** | 1-2 days |

---

## Feature 3: AI Text-to-Speech (TTS) — "AI Dubbing" 🗣️

### What Is It?

After generating a transcript, the tool could **read the text aloud** using an AI voice that sounds like a real person. This could be used for:

- **AI Dubbing**: Translate a transcript and generate speech in another language.
- **Accessibility**: Create audio versions of text content for visually impaired users.
- **Voice Cloning**: Clone a speaker's voice from a 6-second sample and generate new speech in that voice.

### Open-Source TTS Model Comparison

| Model | Voice Quality | Speed | RAM | Voice Cloning? | Best For |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Kokoro** (82M) | ⭐⭐⭐⭐ Great | ⚡ Very Fast | ~300 MB | ❌ No | Fast narration on CPU |
| **XTTS-v2** | ⭐⭐⭐⭐⭐ Excellent | 🟡 Moderate | ~1.5 GB | ✅ Yes (6s sample) | Multilingual voice cloning |
| **ChatTTS** | ⭐⭐⭐⭐ Great | ⚡ Fast | ~800 MB | ❌ No | Conversational / Dialogue |
| **Fish Speech v1.5** | ⭐⭐⭐⭐⭐ Excellent | 🟡 Moderate | ~2 GB | ✅ Yes | Multilingual excellence |
| **Bark** | ⭐⭐⭐ Good | 🔴 Slow | ~2 GB | ❌ No | Emotions / Laughter / Music |
| **Piper** | ⭐⭐⭐ Good | ⚡⚡ Fastest | ~100 MB | ❌ No | Lightweight / Raspberry Pi |

### My Recommendations

1. **For CPU-only environments (like your current setup)**:
   > Use **Kokoro**. It's only 82M parameters, runs blazingly fast on CPU, and produces surprisingly natural-sounding speech. Perfect for generating audio narrations of your transcripts.

2. **For voice cloning ("make it sound like ME")**:
   > Use **XTTS-v2**. Give it a 6-second recording of your voice, and it will generate new speech that sounds like you — in 17+ languages.

3. **For maximum quality (if you have a GPU)**:
   > Use **Fish Speech v1.5**. It produces the most natural, expressive output but requires more compute.

### How It Would Fit Into Our Pipeline

```text
Video ──▶ Audio ──▶ Transcript ──▶ [Translate?] ──▶ TTS ──▶ New Audio Track
                     (Whisper)      (LLM/Translate)   (Kokoro/XTTS)
```

### CLI Example (Proposed)

```bash
# Generate speech from a transcript
python -m media_pipeline_toolkit speak --input transcript.txt --voice kokoro

# Clone a voice and generate speech
python -m media_pipeline_toolkit speak --input transcript.txt --voice xtts --voice-sample my_voice.wav

# Full AI dubbing pipeline: video → transcript → translate → new voice
python -m media_pipeline_toolkit dub --input lecture.mp4 --target-language es --voice kokoro
```

### Complexity

| Aspect | Rating |
| :--- | :--- |
| **Difficulty** | ⭐⭐⭐⭐ High |
| **New Dependencies** | `kokoro` or `TTS` (Coqui) or `fish-speech` |
| **Estimated Time** | 4-5 days |

---

## Feature 4 (Bonus): Translation Layer 🔤

### What Is It?

Whisper can translate audio **to English only**. For translating transcripts into *any* other language, we would need a separate translation step.

### Options

| Approach | Accuracy | Speed | Privacy |
| :--- | :--- | :--- | :--- |
| **Whisper `task=translate`** | Good | Fast | ✅ Local |
| **Argos Translate** (open-source) | Good | Fast | ✅ Local |
| **Meta NLLB-200** (open-source) | Excellent | Moderate | ✅ Local |
| **LLM (Llama 3.1 / Qwen)** | Best | Slow | ✅ Local |
| **Google Translate API** | Excellent | Fast | ❌ Cloud |

### My Recommendation

> Use **Argos Translate** for a lightweight, fully offline translation engine. It supports 50+ languages and runs on CPU. For higher quality, use a local LLM like **Llama 3.1** via `ollama`.

---

## 📊 Priority & Implementation Order

| Priority | Feature | Effort | Value |
| :--- | :--- | :--- | :--- |
| 🥇 **1st** | Multi-Language Audio Tracks | Low | High |
| 🥈 **2nd** | Real-Time Streaming | Medium | High |
| 🥉 **3rd** | Translation Layer | Medium | Medium |
| 4️⃣ **4th** | AI Text-to-Speech / Dubbing | High | Very High |

> [!NOTE]
> The recommended order starts with the **lowest effort, highest impact** features first. Multi-track support requires zero new dependencies. TTS/Dubbing is saved for last because it requires the most research and the heaviest new dependencies.

---

## 🧪 Research Links

| Resource | URL |
| :--- | :--- |
| Kokoro TTS | https://github.com/hexgrad/kokoro |
| XTTS-v2 (Coqui) | https://github.com/coqui-ai/TTS |
| Fish Speech | https://github.com/fishaudio/fish-speech |
| Piper TTS | https://github.com/rhasspy/piper |
| Argos Translate | https://github.com/argosopentech/argos-translate |
| sounddevice | https://github.com/spatialaudio/python-sounddevice |

# Example Commands for Media Pipeline Toolkit

```bash
# 1. Extract audio
python -m media_pipeline_toolkit extract-audio \
  --input "video.mp4" \
  --output "outputs/video/audio.wav"

# 2. Transcribe Video
python -m media_pipeline_toolkit transcribe-video \
  --input "video.mp4" \
  --output-dir "outputs/video-job" \
  --model "base" \
  --language "en" \
  --chunk-seconds 900 \
  --formats txt srt vtt json

# 3. Batch Process
python -m media_pipeline_toolkit batch \
  --input-dir "videos" \
  --output-dir "outputs/batch-run" \
  --model "base" \
  --language "en" \
  --chunk-seconds 900 \
  --formats txt srt vtt json \
  --resume
```

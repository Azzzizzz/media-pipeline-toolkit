import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from media_pipeline_toolkit.media import extract_audio, get_duration_seconds

def test_extract_audio():
    with patch("media_pipeline_toolkit.media.subprocess.run") as mock_run:
        video_path = Path("input.mp4")
        audio_path = Path("output.wav")
        
        extract_audio(video_path, audio_path)
        
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        
        assert cmd[0] == "ffmpeg"
        assert "-vn" in cmd
        assert "-ac" in cmd
        assert cmd[cmd.index("-ac") + 1] == "1"
        assert "-ar" in cmd
        assert cmd[cmd.index("-ar") + 1] == "16000"
        assert str(video_path) in cmd
        assert str(audio_path) in cmd

def test_get_duration_seconds():
    with patch("media_pipeline_toolkit.media.subprocess.run") as mock_run:
        # Create a mock response matching ffprobe's JSON output
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"format": {"duration": "123.45"}})
        mock_run.return_value = mock_result
        
        target_path = Path("input.mp4")
        duration = get_duration_seconds(target_path)
        
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "ffprobe"
        assert "-show_entries" in cmd
        assert str(target_path) in cmd
        
        assert duration == 123.45

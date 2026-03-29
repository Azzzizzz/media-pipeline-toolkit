from pathlib import Path
from unittest.mock import patch, MagicMock
from media_pipeline_toolkit.transcription import Transcriber


def test_transcriber_init():
    with patch("media_pipeline_toolkit.transcription.WhisperModel") as mock_whisper:
        t = Transcriber(model_name="tiny", language="en")
        mock_whisper.assert_called_once_with("tiny", device="cpu", compute_type="int8")
        assert t.model_name == "tiny"
        assert t.language == "en"


def test_transcribe_audio():
    with patch("media_pipeline_toolkit.transcription.WhisperModel") as mock_whisper:
        # Create mock model instance
        mock_instance = MagicMock()
        mock_whisper.return_value = mock_instance
        
        # Create mock Segment and Info objects returned by transcribe
        mock_segment = MagicMock()
        mock_segment.start = 0.5
        mock_segment.end = 2.0
        mock_segment.text = " Hello world. "
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_instance.transcribe.return_value = ([mock_segment], mock_info)
        
        # Test invocation
        t = Transcriber()
        result = t.transcribe_audio(Path("fake.wav"))
        
        # Verify faster-whisper was called cleanly
        mock_instance.transcribe.assert_called_once_with("fake.wav", language=None)
        
        # Verify payload mapping
        assert result["model"] == "base"
        assert result["language"] == "en"
        assert len(result["segments"]) == 1
        assert result["segments"][0]["start"] == 0.5
        assert result["segments"][0]["end"] == 2.0
        assert result["segments"][0]["text"] == "Hello world."

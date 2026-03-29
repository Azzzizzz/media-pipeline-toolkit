import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from media_pipeline_toolkit.pipeline import process_audio_pipeline, process_video_pipeline


@patch("media_pipeline_toolkit.pipeline.get_duration_seconds")
@patch("media_pipeline_toolkit.pipeline.Transcriber")
@patch("media_pipeline_toolkit.pipeline.save_srt")
@patch("media_pipeline_toolkit.pipeline.write_manifest")
def test_process_audio_pipeline_short(mock_manifest, mock_save_srt, mock_transcriber, mock_duration, tmp_path):
    # Setup
    audio_path = tmp_path / "test.wav"
    audio_path.touch()
    output_dir = tmp_path / "output"
    
    mock_duration.return_value = 100.0  # Less than 900s
    
    mock_inst = MagicMock()
    mock_transcriber.return_value = mock_inst
    mock_inst.transcribe_audio.return_value = {"segments": [], "language": "en"}
    
    # Run
    manifest = process_audio_pipeline(audio_path, output_dir, chunk_seconds=900)
    
    # Verify
    assert manifest["status"] == "completed"
    assert manifest["source_type"] == "audio"
    mock_inst.transcribe_audio.assert_called_once_with(audio_path)
    mock_save_srt.assert_called_once()
    mock_manifest.assert_called_once()


@patch("media_pipeline_toolkit.pipeline.extract_audio")
@patch("media_pipeline_toolkit.pipeline.process_audio_pipeline")
@patch("media_pipeline_toolkit.pipeline.write_manifest")
def test_process_video_pipeline(mock_manifest, mock_audio_pipe, mock_extract, tmp_path):
    # Setup
    video_path = tmp_path / "test.mp4"
    video_path.touch()
    output_dir = tmp_path / "output"
    
    mock_audio_pipe.return_value = {"status": "completed"}
    
    # Run
    process_video_pipeline(video_path, output_dir)
    
    # Verify
    mock_extract.assert_called_once()
    mock_audio_pipe.assert_called_once()
    assert mock_manifest.call_count == 1

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from media_pipeline_toolkit.batch import process_directory, is_already_completed


def test_is_already_completed(tmp_path):
    output_dir = tmp_path / "job"
    output_dir.mkdir()
    manifest_path = output_dir / "manifest.json"
    
    # 1. No manifest
    assert not is_already_completed(output_dir)
    
    # 2. Incomplete manifest
    manifest_path.write_text(json.dumps({"status": "failed"}))
    assert not is_already_completed(output_dir)
    
    # 3. Completed manifest
    manifest_path.write_text(json.dumps({"status": "completed"}))
    assert is_already_completed(output_dir)


@patch("media_pipeline_toolkit.batch.process_video_pipeline")
@patch("media_pipeline_toolkit.batch.process_audio_pipeline")
def test_process_directory(mock_audio, mock_video, tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "v.mp4").touch()
    (input_dir / "a.wav").touch()
    (input_dir / "ignore.txt").touch()
    
    output_dir = tmp_path / "output"
    
    # Mock side effects to create directories since the real functions are mocked
    def mock_video_side_effect(video_path, output_dir, **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
    def mock_audio_side_effect(audio_path, output_dir, **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
        
    mock_video.side_effect = mock_video_side_effect
    mock_audio.side_effect = mock_audio_side_effect

    # Run
    process_directory(input_dir, output_dir, resume=False)
    
    # Verify
    assert mock_video.call_count == 1
    assert mock_audio.call_count == 1
    
    # Check that it tried to create separate folders
    assert (output_dir / "v").exists()
    assert (output_dir / "a").exists()


@patch("media_pipeline_toolkit.batch.process_video_pipeline")
def test_process_directory_resume(mock_video, tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "v.mp4").touch()
    
    output_dir = tmp_path / "output"
    job_v_dir = output_dir / "v"
    job_v_dir.mkdir(parents=True)
    (job_v_dir / "manifest.json").write_text(json.dumps({"status": "completed"}))
    
    # Run with resume=True
    process_directory(input_dir, output_dir, resume=True)
    
    # Verify: should skip
    assert mock_video.call_count == 0

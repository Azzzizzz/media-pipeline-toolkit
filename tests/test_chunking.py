from pathlib import Path
from unittest.mock import patch, MagicMock
from media_pipeline_toolkit.chunking import split_audio_into_chunks, merge_chunk_results


def test_split_audio_into_chunks(tmp_path):
    audio_path = tmp_path / "test.wav"
    audio_path.write_text("dummy content")
    
    output_dir = tmp_path / "chunks"
    
    # Mocking subprocess.run to avoid actual ffmpeg call
    # Mocking get_duration_seconds to return a fixed value
    with patch("media_pipeline_toolkit.chunking.subprocess.run") as mock_run, \
         patch("media_pipeline_toolkit.chunking.get_duration_seconds") as mock_duration:
        
        mock_duration.return_value = 10.0
        
        # We need to simulate the creation of chunk files because glob() is called
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "chunk_000.wav").touch()
        (output_dir / "chunk_001.wav").touch()
        
        chunks = split_audio_into_chunks(audio_path, output_dir, chunk_seconds=10)
        
        assert len(chunks) == 2
        assert chunks[0] == (output_dir / "chunk_000.wav", 0.0)
        assert chunks[1] == (output_dir / "chunk_001.wav", 10.0)
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "-segment_time" in args
        assert "10" in args


def test_merge_chunk_results():
    # Setup mock chunks
    chunks = [
        (Path("chunk1.wav"), 0.0),
        (Path("chunk2.wav"), 10.0)
    ]
    
    # Setup mock transcriber
    mock_transcriber = MagicMock()
    mock_transcriber.transcribe_audio.side_effect = [
        {"segments": [{"start": 1.0, "end": 2.0, "text": "Hello"}]},
        {"segments": [{"start": 0.5, "end": 1.5, "text": "World"}]}
    ]
    
    results = merge_chunk_results(chunks, mock_transcriber)
    
    assert len(results) == 2
    # First chunk: start 1.0 + 0.0 = 1.0
    assert results[0]["start"] == 1.0
    assert results[0]["text"] == "Hello"
    
    # Second chunk: start 0.5 + 10.0 = 10.5
    assert results[1]["start"] == 10.5
    assert results[1]["text"] == "World"

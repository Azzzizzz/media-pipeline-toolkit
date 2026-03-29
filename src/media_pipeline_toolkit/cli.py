import argparse
import logging
import sys
from pathlib import Path

from media_pipeline_toolkit.pipeline import process_video_pipeline, process_audio_pipeline
from media_pipeline_toolkit.batch import process_directory
from media_pipeline_toolkit.config import load_config_file, merge_config
from media_pipeline_toolkit.logging_utils import setup_logging


def main() -> int:
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Media Pipeline Toolkit - extract audio and generate transcripts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. extract-audio
    p_extract = subparsers.add_parser("extract-audio", help="Extract audio from video")
    p_extract.add_argument("--input", required=True, type=Path, help="Input video file")
    p_extract.add_argument("--output", required=True, type=Path, help="Output audio file")

    # 2. transcribe-audio
    p_trans_a = subparsers.add_parser("transcribe-audio", help="Transcribe audio file")
    p_trans_a.add_argument("--input", required=True, type=Path, help="Input audio file")
    p_trans_a.add_argument("--output-dir", type=Path, help="Output directory")
    p_trans_a.add_argument("--model", default="base", help="Whisper model name")
    p_trans_a.add_argument("--language", help="Source language")
    p_trans_a.add_argument("--formats", nargs="+", help="Output formats (txt, srt, vtt, json)")
    p_trans_a.add_argument("--chunk-seconds", type=int, default=900, help="Chunk length in seconds")

    # 3. transcribe-video
    p_trans_v = subparsers.add_parser("transcribe-video", help="Transcribe video directly")
    p_trans_v.add_argument("--input", required=True, type=Path, help="Input video file")
    p_trans_v.add_argument("--output-dir", type=Path, help="Output directory")
    p_trans_v.add_argument("--model", default="base", help="Whisper model name")
    p_trans_v.add_argument("--language", help="Source language")
    p_trans_v.add_argument("--formats", nargs="+", help="Output formats (txt, srt, vtt, json)")
    p_trans_v.add_argument("--chunk-seconds", type=int, default=900, help="Chunk length in seconds")

    # 4. batch
    p_batch = subparsers.add_parser("batch", help="Process a directory of files")
    p_batch.add_argument("--input-dir", required=True, type=Path, help="Input directory")
    p_batch.add_argument("--output-dir", required=True, type=Path, help="Output root directory")
    p_batch.add_argument("--model", default="base", help="Whisper model name")
    p_batch.add_argument("--language", help="Source language")
    p_batch.add_argument("--formats", nargs="+", help="Output formats (txt, srt, vtt, json)")
    p_batch.add_argument("--chunk-seconds", type=int, default=900, help="Chunk length in seconds")
    p_batch.add_argument("--resume", action="store_true", help="Resume completed jobs")

    # 5. run (config file mode)
    p_run = subparsers.add_parser("run", help="Run a job from a config file")
    p_run.add_argument("--config", required=True, type=Path, help="Path to job.yaml")

    args = parser.parse_args()

    try:
        if args.command == "extract-audio":
            from media_pipeline_toolkit.media import extract_audio
            extract_audio(args.input, args.output)
            print(f"Extracted audio to {args.output}")

        elif args.command == "transcribe-audio":
            out_dir = args.output_dir or args.input.parent / args.input.stem
            process_audio_pipeline(
                audio_path=args.input,
                output_dir=out_dir,
                model_name=args.model,
                language=args.language,
                chunk_seconds=args.chunk_seconds,
                formats=args.formats,
            )

        elif args.command == "transcribe-video":
            out_dir = args.output_dir or args.input.parent / args.input.stem
            process_video_pipeline(
                video_path=args.input,
                output_dir=out_dir,
                model_name=args.model,
                language=args.language,
                chunk_seconds=args.chunk_seconds,
                formats=args.formats,
            )

        elif args.command == "batch":
            process_directory(
                input_dir=args.input_dir,
                output_dir=args.output_dir,
                model_name=args.model,
                language=args.language,
                chunk_seconds=args.chunk_seconds,
                formats=args.formats,
                resume=args.resume,
            )

        elif args.command == "run":
            config_data = load_config_file(args.config)
            # For simplicity, if it is a 'run' command, we just execute based on config
            # A more robust version would map job_type to the functions above
            job_type = config_data.get("job_type", "transcribe-video")
            input_path = Path(config_data.get("input", ""))
            output_dir = Path(config_data.get("output_dir", str(input_path.parent / input_path.stem)))
            
            if job_type == "transcribe-video":
                process_video_pipeline(
                    video_path=input_path,
                    output_dir=output_dir,
                    model_name=config_data.get("model", "base"),
                    language=config_data.get("language"),
                    chunk_seconds=config_data.get("chunk_seconds", 900),
                    formats=config_data.get("formats"),
                )
            elif job_type == "batch":
                process_directory(
                    input_dir=Path(config_data.get("input_dir", ".")),
                    output_dir=Path(config_data.get("output_dir", "outputs")),
                    model_name=config_data.get("model", "base"),
                    language=config_data.get("language"),
                    chunk_seconds=config_data.get("chunk_seconds", 900),
                    formats=config_data.get("formats"),
                    resume=config_data.get("resume", False),
                )
            # Add other job types as needed

    except Exception as e:
        logging.getLogger("cli").error(f"Error: {e}")
        return 1

    return 0


"""
Configuration parsing and default management.
"""
import yaml
from pathlib import Path


def load_config_file(config_path: Path) -> dict:
    """
    Loads a YAML configuration file.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def merge_config(cli_args: dict, config_data: dict) -> dict:
    """
    Merges CLI arguments with config file data. 
    CLI args have precedence.
    """
    # Define defaults
    final_config = {
        "model": "base",
        "language": None,
        "chunk_seconds": 900,
        "formats": ["txt", "srt", "vtt", "json"],
        "resume": False,
        "overwrite": False,
    }

    # Override with config file
    final_config.update(config_data)

    # Override with CLI args (only if they are not None)
    for key, value in cli_args.items():
        if value is not None:
            final_config[key] = value

    return final_config


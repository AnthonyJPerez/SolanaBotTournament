from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Union

def load_json(path: Path, default: Any) -> Any:
    """Load JSON file with error handling and fallback to default."""
    if not path.exists():
        return default
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, IOError) as e:
        logging.error(f"Failed to load JSON from {path}: {e}")
        return default

def save_json(path: Path, data: Any) -> bool:
    """Save data to JSON file with error handling."""
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (OSError, IOError, TypeError) as e:
        logging.error(f"Failed to save JSON to {path}: {e}")
        return False
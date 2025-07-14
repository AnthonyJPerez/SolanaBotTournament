import pytest
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from solana_bot_tournament.persistence import load_json, save_json


def test_save_and_load_json():
    test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
    
    with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    
    try:
        # Save data
        save_json(temp_path, test_data)
        
        # Load data back
        loaded_data = load_json(temp_path, {})
        
        assert loaded_data == test_data
    finally:
        temp_path.unlink(missing_ok=True)


def test_load_json_default():
    non_existent_path = Path("does_not_exist.json")
    default_value = {"default": True}
    
    result = load_json(non_existent_path, default_value)
    assert result == default_value


def test_load_json_existing_file():
    test_data = {"existing": "data"}
    
    with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)
    
    try:
        result = load_json(temp_path, {"default": "fallback"})
        assert result == test_data
    finally:
        temp_path.unlink(missing_ok=True)
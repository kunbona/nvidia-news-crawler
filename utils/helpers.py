"""
Helper utilities
"""
import json
import yaml
from typing import Dict, Any
from pathlib import Path
from loguru import logger


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_file: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_file}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file}")
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}


def save_json(data: Any, filepath: str) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath: File path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON: {str(e)}")
        return False


def load_json(filepath: str) -> Any:
    """
    Load data from JSON file
    
    Args:
        filepath: File path
        
    Returns:
        Loaded data or None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON from {filepath}")
        return data
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        return None

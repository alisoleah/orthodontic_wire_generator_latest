
# ================================================================
# utils/file_utils.py
"""File I/O utilities for the wire generator."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

class FileUtils:
    """Utilities for file operations and data persistence."""
    
    @staticmethod
    def ensure_directory(filepath: str) -> str:
        """Ensure directory exists for the given filepath."""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        return filepath
    
    @staticmethod
    def get_safe_filename(filename: str, max_length: int = 255) -> str:
        """Get a safe filename by removing invalid characters."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Truncate if too long
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        
        return filename
    
    @staticmethod
    def add_timestamp_to_filename(filename: str) -> str:
        """Add timestamp to filename to avoid conflicts."""
        path = Path(filename)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_name = f"{path.stem}_{timestamp}{path.suffix}"
        return str(path.parent / new_name)
    
    @staticmethod
    def save_json(data: Dict[Any, Any], filename: str) -> bool:
        """Save data to JSON file with error handling."""
        try:
            FileUtils.ensure_directory(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False
    
    @staticmethod
    def load_json(filename: str) -> Optional[Dict[Any, Any]]:
        """Load data from JSON file with error handling."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict[str, Any]:
        """Get detailed file information."""
        if not os.path.exists(filepath):
            return {'exists': False}
        
        stat = os.stat(filepath)
        return {
            'exists': True,
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified_time': time.ctime(stat.st_mtime),
            'created_time': time.ctime(stat.st_ctime),
            'extension': Path(filepath).suffix.lower(),
            'basename': os.path.basename(filepath)
        }
    
    @staticmethod
    def backup_file(filepath: str) -> Optional[str]:
        """Create a backup of a file."""
        if not os.path.exists(filepath):
            return None
        
        backup_path = FileUtils.add_timestamp_to_filename(filepath + '.backup')
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
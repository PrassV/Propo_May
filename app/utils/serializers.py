from datetime import datetime
import json
from typing import Any, Dict

def serialize_datetime(dt: datetime) -> str:
    """Convert datetime to ISO format string"""
    return dt.isoformat() if dt else None

def serialize_for_supabase(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare dictionary data for Supabase by ensuring all values are JSON serializable.
    Converts datetime objects to ISO format strings.
    
    Args:
        data: Dictionary possibly containing datetime objects
        
    Returns:
        Dictionary with all values JSON serializable
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = serialize_datetime(value)
        elif isinstance(value, dict):
            result[key] = serialize_for_supabase(value)
        else:
            result[key] = value
            
    return result 
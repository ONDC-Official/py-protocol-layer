def clean_nones(value):
    """
    Recursively remove all None values from dictionaries and lists, and returns
    the result as a new dictionary or list.
    """
    if isinstance(value, list):
        return [clean_nones(x) for x in value if x is not None]
    elif isinstance(value, dict):
        return {
            key: clean_nones(val)
            for key, val in value.items()
            if val is not None
        }
    else:
        return value


# utils/json_utils.py
import json
from datetime import datetime
from bson import ObjectId
from typing import Any, Union, Dict

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle special types"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

def serialize_to_json(obj: Any) -> str:
    """Serialize an object to JSON string"""
    return json.dumps(obj, cls=JSONEncoder)

def deserialize_from_json(json_str: str) -> Any:
    """Deserialize JSON string to object"""
    return json.loads(json_str)

def make_serializable(obj: Any) -> Any:
    """Convert an object to a JSON-serializable format"""
    if isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, 'to_dict'):
        return make_serializable(obj.to_dict())
    return obj

import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings

def get_service_state(service_id: str, environment: str) -> Optional[Dict[str, Any]]:
    """
    Read-only tool: Retrieve current service state from synthetic fixtures.
    """
    file_path = settings.FIXTURES_DIR / "service_states.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    key = f"{service_id}:{environment}"
    return data.get(key)

def get_deployment_policy(service_id: str, environment: str) -> Optional[Dict[str, Any]]:
    """
    Read-only tool: Retrieve deployment policy from synthetic fixtures.
    """
    file_path = settings.FIXTURES_DIR / "deployment_policies.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    key = f"{service_id}:{environment}"
    return data.get(key)

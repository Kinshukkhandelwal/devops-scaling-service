from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class PlanRequest(BaseModel):
    service_id: str = Field(..., example="payment-service")
    environment: str = Field(..., example="development")
    desired_replicas: int = Field(..., ge=0, example=3)
    reason: str = Field(..., example="Scaling for projected traffic spike.")

class ChangeArtifact(BaseModel):
    service_id: str
    environment: str
    previous_replicas: int
    proposed_replicas: int

class PlanResponse(BaseModel):
    decision: Literal["allowed", "requires_approval", "blocked", "no_change"]
    current_state: Dict[str, Any]
    requested_state: Dict[str, Any]
    evidence_references: List[str]
    explanation: str
    verification_steps: List[str]
    rollback_steps: List[str]
    change_artifact: Optional[ChangeArtifact] = None

from typing import Tuple, Optional, Dict, Any, List
from app.models import ChangeArtifact

def evaluate_scaling_policy(
    service_id: str,
    environment: str,
    desired_replicas: int,
    state: Optional[Dict[str, Any]],
    policy: Optional[Dict[str, Any]]
) -> Tuple[str, Optional[ChangeArtifact], str, List[str]]:
    """
    Evaluates scaling policy deterministically in application code (AC2, AC3, AC4).
    Precedence order:
    1. Missing/invalid state or policy fails safely -> blocked
    2. Out-of-range requests are blocked
    3. Already-matching replica count -> no_change
    4. Increases above error rate threshold (>5%) -> blocked
    5. Production changes -> requires_approval
    6. Otherwise -> allowed
    """
    # Rule 1: Missing/invalid state or policy
    if not state or not policy:
        reason = f"Missing or invalid telemetry/policy for service '{service_id}' in environment '{environment}'."
        return "blocked", None, reason, ["Ensure service telemetry and policy fixtures are registered."]

    current_replicas = state.get("current_replicas", 0)
    error_rate = state.get("error_rate", 0.0)
    
    # Environment replica range checks
    if environment.lower() == "development":
        min_rep, max_rep = policy.get("min_replicas", 1), policy.get("max_replicas", 5)
    elif environment.lower() == "production":
        min_rep, max_rep = policy.get("min_replicas", 2), policy.get("max_replicas", 10)
    else:
        min_rep, max_rep = policy.get("min_replicas", 1), policy.get("max_replicas", 5)

    # Rule 2: Out-of-range requests
    if desired_replicas < min_rep or desired_replicas > max_rep:
        reason = (f"Requested replica count {desired_replicas} is out of permitted range "
                  f"[{min_rep}-{max_rep}] for {environment}.")
        return "blocked", None, reason, ["Submit a request within valid replica boundaries."]

    # Rule 3: Already-matching replica count
    if desired_replicas == current_replicas:
        reason = f"Current replicas ({current_replicas}) already matches requested count ({desired_replicas})."
        return "no_change", None, reason, ["No action needed."]

    # Rule 4: Increases above error threshold (5% / 0.05)
    max_error_thresh = policy.get("max_error_rate_threshold", 0.05)
    is_increase = desired_replicas > current_replicas
    if is_increase and error_rate > max_error_thresh:
        reason = (f"Unhealthy scale-up blocked: error rate is {error_rate*100:.1f}%, "
                  f"which exceeds the safety threshold of {max_error_thresh*100:.1f}%.")
        return "blocked", None, reason, ["Investigate error rates before attempting scaling."]

    # Construct artifact for actionable decisions
    artifact = ChangeArtifact(
        service_id=service_id,
        environment=environment,
        previous_replicas=current_replicas,
        proposed_replicas=desired_replicas
    )

    # Rule 5: Production changes require approval
    if environment.lower() == "production" or policy.get("requires_human_approval", False):
        reason = f"Production scaling from {current_replicas} to {desired_replicas} requires human approval."
        return "requires_approval", artifact, reason, ["Submit proposal for DevOps/SRE lead review."]

    # Rule 6: Otherwise allowed
    reason = f"Scaling request from {current_replicas} to {desired_replicas} in {environment} is allowed by policy."
    return "allowed", artifact, reason, ["Apply change via deployment pipeline."]

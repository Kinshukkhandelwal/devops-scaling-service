import logging
from typing import Dict, Any, List, Optional
from app.tools import get_service_state, get_deployment_policy
from app.policy import evaluate_scaling_policy
from app.models import PlanRequest, PlanResponse, ChangeArtifact

logger = logging.getLogger("scaling_agent")

class ReplicaScalingAgent:
    """
    Agent responsible for executing read-only tools, inspecting service state and policy,
    generating narrative recommendations, and delegating safety evaluation to policy code.
    """

    def __init__(self, provider: str = "double"):
        self.provider = provider

    def run(self, request: PlanRequest) -> PlanResponse:
        # Step 1: Agent selects and executes read-only tools
        service_state = get_service_state(request.service_id, request.environment)
        deployment_policy = get_deployment_policy(request.service_id, request.environment)

        # Gather evidence references
        evidence_refs = []
        if service_state and "fixture_id" in service_state:
            evidence_refs.append(service_state["fixture_id"])
        if deployment_policy and "fixture_id" in deployment_policy:
            evidence_refs.append(deployment_policy["fixture_id"])

        # Step 2: Policy Enforcement in Application Code (Deterministic Guardrails AC2-AC5)
        decision, change_artifact, policy_reason, verification_suggestions = evaluate_scaling_policy(
            service_id=request.service_id,
            environment=request.environment,
            desired_replicas=request.desired_replicas,
            state=service_state,
            policy=deployment_policy
        )

        # Step 3: Generate Agent Contextual Explanation & Verification/Rollback Guidance
        current_replicas = service_state.get("current_replicas", "unknown") if service_state else "unknown"
        error_rate = service_state.get("error_rate", 0.0) if service_state else 0.0

        explanation = (
            f"Agent analyzed request for service '{request.service_id}' ({request.environment}) "
            f"requesting {request.desired_replicas} replicas (current: {current_replicas}, error rate: {error_rate*100:.1f}%). "
            f"Reason provided: '{request.reason}'. "
            f"Policy evaluation outcome: {policy_reason}"
        )

        verification_steps = [
            f"1. Verify HTTP health status for {request.service_id} after deployment.",
            f"2. Confirm replica count in environment metrics equals target ({request.desired_replicas if decision in ['allowed', 'requires_approval'] else current_replicas}).",
            "3. Monitor 5-minute error rate and p95 latency thresholds."
        ] + verification_suggestions

        rollback_steps = [
            f"1. Issue rollback command to reset replicas to previous state ({current_replicas}).",
            "2. Verify service stability and drain pending connections.",
            "3. Log incident in telemetry dashboard for post-mortem."
        ]

        current_state_dict = service_state if service_state else {"status": "not_found"}
        requested_state_dict = {
            "service_id": request.service_id,
            "environment": request.environment,
            "desired_replicas": request.desired_replicas,
            "reason": request.reason
        }

        return PlanResponse(
            decision=decision,
            current_state=current_state_dict,
            requested_state=requested_state_dict,
            evidence_references=evidence_refs,
            explanation=explanation,
            verification_steps=verification_steps,
            rollback_steps=rollback_steps,
            change_artifact=change_artifact
        )

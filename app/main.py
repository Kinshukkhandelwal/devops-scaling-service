from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.models import PlanRequest, PlanResponse
from app.agent import ReplicaScalingAgent

app = FastAPI(
    title="DevOps Replica Scaling Service",
    version="1.0.0",
    description="Local service for converting replica-scaling requests into reviewable change plans with AI agent inspection and deterministic safeguards."
)

def verify_api_token(x_api_token: str = Header(None, alias="X-API-Token")):
    """
    Validates shared API token supplied in X-API-Token request header.
    """
    if not x_api_token or x_api_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Token request header."
        )

@app.post(
    "/plan",
    response_model=PlanResponse,
    dependencies=[Depends(verify_api_token)],
    summary="Generate reviewable replica scaling change plan"
)
async def create_scaling_plan(request: PlanRequest):
    """
    Accepts replica scaling requests, runs read-only tool inspection via agent,
    evaluates policy guardrails, and returns a structured change plan.
    """
    try:
        agent = ReplicaScalingAgent(provider=settings.MODEL_PROVIDER)
        response = agent.run(request)
        return response
    except Exception as e:
        # Controlled failure without exposing raw stack traces or secrets (AC6)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal processing error during plan creation.",
                "error_code": "PLAN_CREATION_FAILED"
            }
        )

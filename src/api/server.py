"""
Syntheget REST API Server
Exposes inspection endpoints for enterprise LLMs and telemetry gateways.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

import sys
import os

# Ensure parent directory is in path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.validators.telemetry_validator import TelemetryValidator
from src.sanitizers.prompt_sanitizer import PromptSanitizer

app = FastAPI(
    title="Syntheget Governance & Security Proxy API",
    description="Stateless runtime proxy endpoint for AI agent safety and telemetry validation.",
    version="0.1.0"
)

validator = TelemetryValidator()
sanitizer = PromptSanitizer()

class InspectionRequest(BaseModel):
    telemetry: Dict[str, Any] = Field(..., description="Sensor or operational metadata payload")
    prompt: str = Field(..., description="Incoming user or agent system prompt")

class InspectionResponse(BaseModel):
    execution_allowed: bool
    status: str
    telemetry_valid: bool
    prompt_sanitized: str
    injection_detected: bool

@app.get("/health")
def health_check():
    """Returns proxy operational readiness status."""
    return {"status": "HEALTHY", "service": "Syntheget-Runtime-Proxy"}

@app.post("/v1/inspect", response_model=InspectionResponse)
def inspect_payload(request: InspectionRequest):
    """
    Primary endpoint: Inspects telemetry provenance and sanitizes prompt context
    prior to model execution.
    """
    is_valid_telemetry, val_reason = validator.validate({"telemetry": request.telemetry})
    sanitized_prompt, injection_detected = sanitizer.sanitize(request.prompt)

    execution_allowed = is_valid_telemetry and not injection_detected
    
    status_code = "APPROVED" if execution_allowed else f"REJECTED_{val_reason}"
    if injection_detected and is_valid_telemetry:
        status_code = "REJECTED_PROMPT_INJECTION_DETECTED"

    return InspectionResponse(
        execution_allowed=execution_allowed,
        status=status_code,
        telemetry_valid=is_valid_telemetry,
        prompt_sanitized=sanitized_prompt,
        injection_detected=injection_detected
    )

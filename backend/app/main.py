from fastapi import FastAPI
from pydantic import BaseModel, Field

# ==========================================================
# Import Security Detection Modules
# ==========================================================

from app.detection.rule_detector import detect_rule_based
from app.detection.transformer_detector import detect_transformer

from app.risk_engine.risk_scoring import calculate_risk_level
from app.risk_engine.decision_engine import make_security_decision


# ==========================================================
# Initialize FastAPI Application
# ==========================================================

app = FastAPI(
    title="AI-Based LLM Security Firewall",
    description="Detection and Mitigation of Prompt Injection and Jailbreak Attacks",
    version="1.2.0"
)


# ==========================================================
# Home Endpoint
# ==========================================================

@app.get("/")
def home():
    return {
        "project": "AI-Based LLM Security Firewall",
        "status": "running",
        "message": "Security Framework API is active",
        "version": "1.2.0"
    }


# ==========================================================
# Health Check Endpoint
# ==========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LLM Security Firewall"
    }


# ==========================================================
# Request Model
# ==========================================================

class PromptRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User prompt to analyze for security threats"
    )


# ==========================================================
# Rule-Based Prompt Security Analysis Endpoint
# ==========================================================

@app.post("/analyze")
def analyze_prompt(request: PromptRequest):

    # STEP 1: Rule-Based Attack Detection
    detection_result = detect_rule_based(request.prompt)

    # STEP 2: Extract Risk Score
    risk_score = detection_result["risk_score"]

    # STEP 3: Calculate Risk Severity
    risk_level = calculate_risk_level(risk_score)

    # STEP 4: Make Security Decision
    decision = make_security_decision(risk_score)

    # STEP 5: Return Complete Security Analysis
    return {
        "prompt": request.prompt,
        "attack_detected": detection_result["attack_detected"],
        "attack_type": detection_result["attack_type"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "matched_rules": detection_result["matched_rules"],
        "detection_method": "rule_based"
    }


# ==========================================================
# Transformer-Based Prompt Security Analysis Endpoint
# ==========================================================

@app.post("/analyze/transformer")
def analyze_transformer(request: PromptRequest):

    # STEP 1: DistilBERT-Based Attack Detection
    detection_result = detect_transformer(request.prompt)

    # STEP 2: Return Transformer Detection Results
    return {
        "prompt": request.prompt,
        "attack_detected": detection_result["attack_detected"],
        "attack_type": detection_result["attack_type"],
        "confidence": detection_result["confidence"],
        "malicious_probability": detection_result["malicious_probability"],
        "detection_method": detection_result["detection_method"]
    }
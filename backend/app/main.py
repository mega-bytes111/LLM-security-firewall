import httpx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ==========================================================
# Import Security Detection Modules
# ==========================================================

from app.detection.rule_detector import detect_rule_based
from app.detection.transformer_detector import detect_transformer
from app.detection.logistic_detector import detect_logistic
from app.detection.hybrid_detector import detect_hybrid

from app.risk_engine.risk_scoring import calculate_risk_level
from app.risk_engine.decision_engine import make_security_decision

# ==========================================================
# Import Local LLM Client
# ==========================================================

from app.llm.ollama_client import generate_response


# ==========================================================
# Initialize FastAPI Application
# ==========================================================

app = FastAPI(
    title="AI-Based LLM Security Firewall",
    description=(
        "Detection and Mitigation of Prompt Injection "
        "and Jailbreak Attacks"
    ),
    version="1.2.0",
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
        "version": "1.2.0",
    }


# ==========================================================
# Health Check Endpoint
# ==========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LLM Security Firewall",
    }


# ==========================================================
# Request Model
# ==========================================================

class PromptRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User prompt to analyze for security threats",
    )


# ==========================================================
# Rule-Based Prompt Security Analysis Endpoint
# ==========================================================

@app.post("/analyze")
def analyze_prompt(request: PromptRequest):

    detection_result = detect_rule_based(request.prompt)

    risk_score = detection_result["risk_score"]

    risk_level = calculate_risk_level(risk_score)

    decision = make_security_decision(risk_score)

    return {
        "prompt": request.prompt,
        "attack_detected": detection_result["attack_detected"],
        "attack_type": detection_result["attack_type"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "matched_rules": detection_result["matched_rules"],
        "detection_method": "rule_based",
    }


# ==========================================================
# Transformer-Based Prompt Security Analysis Endpoint
# ==========================================================

@app.post("/analyze/transformer")
def analyze_transformer(request: PromptRequest):

    detection_result = detect_transformer(request.prompt)

    return {
        "prompt": request.prompt,
        "attack_detected": detection_result["attack_detected"],
        "attack_type": detection_result["attack_type"],
        "confidence": detection_result["confidence"],
        "malicious_probability": detection_result["malicious_probability"],
        "detection_method": detection_result["detection_method"],
    }


# ==========================================================
# Logistic Regression Prompt Security Analysis Endpoint
# ==========================================================

@app.post("/analyze/logistic")
def analyze_logistic(request: PromptRequest):

    detection_result = detect_logistic(request.prompt)

    return {
        "prompt": request.prompt,
        "attack_detected": detection_result["attack_detected"],
        "attack_type": detection_result["attack_type"],
        "confidence": detection_result["confidence"],
        "malicious_probability": detection_result["malicious_probability"],
        "detection_method": detection_result["detection_method"],
    }


# ==========================================================
# Hybrid Prompt Security Analysis Endpoint
# ==========================================================

@app.post("/analyze/hybrid")
def analyze_hybrid(request: PromptRequest):

    result = detect_hybrid(request.prompt)

    return {
        "prompt": request.prompt,
        "evidence": result["evidence"],
        "policy_result": result["policy_result"],
        "detection_method": "hybrid",
    }


# ==========================================================
# Firewall-Protected Local LLM Endpoint
# ==========================================================

@app.post("/chat/protected")
def chat_protected(request: PromptRequest):

    # STEP 1: Analyze using the preselected DistilBERT policy.
    detection = detect_transformer(request.prompt)

    # STEP 2: If flagged, block without calling the LLM.
    if detection["attack_detected"]:
        return {
            "decision": "BLOCK",
            "detection_method": "distilbert",
            "message": "Prompt blocked by the security firewall.",
            "llm_response": None,
        }

    # STEP 3: If allowed, forward the prompt to Ollama.
    try:
        llm_response = generate_response(request.prompt)

    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Local LLM is unavailable or returned "
                "an invalid response."
            ),
        ) from exc

    return {
        "decision": "ALLOW",
        "detection_method": "distilbert",
        "message": "Prompt allowed by the security firewall.",
        "llm_response": llm_response,
    }
def make_security_decision(risk_score: float) -> str:

    BLOCK_THRESHOLD = 0.75

    if risk_score >= BLOCK_THRESHOLD:
        return "BLOCK"

    return "ALLOW"
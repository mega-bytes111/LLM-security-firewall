def calculate_risk_level(risk_score: float) -> str:

    if risk_score >= 0.90:
        return "CRITICAL"

    elif risk_score >= 0.75:
        return "HIGH"

    elif risk_score >= 0.40:
        return "MEDIUM"

    else:
        return "LOW"
from app.detection.rule_detector import detect_rule_based
from app.detection.logistic_detector import detect_logistic
from app.detection.transformer_detector import detect_transformer

from app.risk_engine.hybrid_policy import apply_or_policy


def detect_hybrid(prompt: str) -> dict:
    """
    Collect detector outputs and apply the candidate OR policy.

    Rule scores and model scores remain separate; they are not
    combined into a single probability.
    """

    rule_result = detect_rule_based(prompt)
    logistic_result = detect_logistic(prompt)
    transformer_result = detect_transformer(prompt)

    policy_result = apply_or_policy(
        rule_detected=rule_result["attack_detected"],
        logistic_detected=logistic_result["attack_detected"],
        transformer_detected=transformer_result["attack_detected"],
    )

    return {
        "evidence": {
            "rule_based": {
                "attack_detected": rule_result["attack_detected"],
                "attack_type": rule_result["attack_type"],
                "heuristic_risk_score": rule_result["risk_score"],
                "matched_rules": rule_result["matched_rules"],
            },
            "logistic_regression": logistic_result,
            "distilbert": transformer_result,
        },
        "policy_result": policy_result,
    }
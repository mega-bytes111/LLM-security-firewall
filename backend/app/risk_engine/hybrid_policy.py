def apply_or_policy(
    rule_detected: bool,
    logistic_detected: bool,
    transformer_detected: bool,
) -> dict:
    """
    Candidate OR policy.

    BLOCK if any detector flags the prompt.
    This policy is intended for evaluation, not guaranteed protection.
    """

    triggers = []

    if rule_detected:
        triggers.append("rule_based")

    if logistic_detected:
        triggers.append("logistic_regression")

    if transformer_detected:
        triggers.append("distilbert")

    return {
        "decision": "BLOCK" if triggers else "ALLOW",
        "triggered_by": triggers,
        "policy": "any_detector_flags",
    }
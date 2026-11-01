import app.detection.hybrid_detector as hybrid


def test_hybrid_blocks_when_logistic_flags(monkeypatch):
    monkeypatch.setattr(
        hybrid,
        "detect_rule_based",
        lambda prompt: {
            "attack_detected": False,
            "attack_type": "benign",
            "risk_score": 0.0,
            "matched_rules": [],
        },
    )

    monkeypatch.setattr(
        hybrid,
        "detect_logistic",
        lambda prompt: {
            "attack_detected": True,
            "attack_type": "malicious",
            "confidence": 0.8,
            "malicious_probability": 0.8,
            "detection_method": "logistic_regression",
        },
    )

    monkeypatch.setattr(
        hybrid,
        "detect_transformer",
        lambda prompt: {
            "attack_detected": False,
            "attack_type": "benign",
            "confidence": 0.7,
            "malicious_probability": 0.3,
            "detection_method": "distilbert",
        },
    )

    result = hybrid.detect_hybrid("Example prompt")

    assert result["policy_result"]["decision"] == "BLOCK"
    assert result["policy_result"]["triggered_by"] == [
        "logistic_regression"
    ]
    assert result["evidence"]["rule_based"]["attack_detected"] is False
    assert result["evidence"]["logistic_regression"]["attack_detected"] is True


def test_hybrid_allows_when_none_flag(monkeypatch):
    monkeypatch.setattr(
        hybrid,
        "detect_rule_based",
        lambda prompt: {
            "attack_detected": False,
            "attack_type": "benign",
            "risk_score": 0.0,
            "matched_rules": [],
        },
    )

    monkeypatch.setattr(
        hybrid,
        "detect_logistic",
        lambda prompt: {"attack_detected": False},
    )

    monkeypatch.setattr(
        hybrid,
        "detect_transformer",
        lambda prompt: {"attack_detected": False},
    )

    result = hybrid.detect_hybrid("Example prompt")

    assert result["policy_result"]["decision"] == "ALLOW"
    assert result["policy_result"]["triggered_by"] == []
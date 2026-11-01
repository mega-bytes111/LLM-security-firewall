import pytest

from app.risk_engine.hybrid_policy import apply_or_policy


@pytest.mark.parametrize(
    "rule, logistic, transformer, expected_decision, expected_triggers",
    [
        (False, False, False, "ALLOW", []),
        (True, False, False, "BLOCK", ["rule_based"]),
        (False, True, False, "BLOCK", ["logistic_regression"]),
        (False, False, True, "BLOCK", ["distilbert"]),
        (
            True,
            True,
            True,
            "BLOCK",
            ["rule_based", "logistic_regression", "distilbert"],
        ),
    ],
)
def test_or_policy(
    rule,
    logistic,
    transformer,
    expected_decision,
    expected_triggers,
):
    result = apply_or_policy(rule, logistic, transformer)

    assert result["decision"] == expected_decision
    assert result["triggered_by"] == expected_triggers
    assert result["policy"] == "any_detector_flags"
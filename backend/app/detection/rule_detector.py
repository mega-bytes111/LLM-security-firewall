import re

from app.utils.preprocessing import preprocess_prompt


ATTACK_RULES = {
    "system_prompt_extraction": [
        {
            "pattern": r"reveal (your )?(hidden )?system prompt",
            "score": 0.95
        },
        {
            "pattern": r"show (me )?(your )?system instructions",
            "score": 0.90
        },
        {
            "pattern": r"print (your )?(internal )?instructions",
            "score": 0.90
        },
        {
            "pattern": r"disclose (your )?(hidden )?instructions",
            "score": 0.95
        }
    ],

    "instruction_manipulation": [
        {
            "pattern": r"ignore (all )?(your )?previous instructions",
            "score": 0.90
        },
        {
            "pattern": r"disregard (all )?(your )?previous instructions",
            "score": 0.90
        },
        {
            "pattern": r"override (your )?system instructions",
            "score": 0.95
        },
        {
            "pattern": r"forget (all )?(your )?previous instructions",
            "score": 0.85
        }
    ],

    "jailbreak": [
        {
            "pattern": r"bypass (your )?(safety )?restrictions",
            "score": 0.95
        },
        {
            "pattern": r"disable (your )?safety filters",
            "score": 0.95
        },
        {
            "pattern": r"act as an unrestricted ai",
            "score": 0.90
        },
        {
            "pattern": r"you are now in developer mode",
            "score": 0.85
        }
    ],

    "prompt_injection": [
        {
            "pattern": r"new system instruction",
            "score": 0.90
        },
        {
            "pattern": r"system message override",
            "score": 0.95
        },
        {
            "pattern": r"ignore the original task",
            "score": 0.90
        },
        {
            "pattern": r"follow these instructions instead",
            "score": 0.85
        }
    ]
}


def detect_rule_based(prompt: str) -> dict:

    processed_prompt = preprocess_prompt(prompt)

    detected_attacks = []

    for attack_type, rules in ATTACK_RULES.items():

        for rule in rules:

            if re.search(rule["pattern"], processed_prompt):

                detected_attacks.append({
                    "attack_type": attack_type,
                    "risk_score": rule["score"],
                    "matched_pattern": rule["pattern"]
                })

    if not detected_attacks:

        return {
            "attack_detected": False,
            "attack_type": "benign",
            "risk_score": 0.0,
            "matched_rules": []
        }

    highest_risk_attack = max(
        detected_attacks,
        key=lambda attack: attack["risk_score"]
    )

    return {
        "attack_detected": True,
        "attack_type": highest_risk_attack["attack_type"],
        "risk_score": highest_risk_attack["risk_score"],
        "matched_rules": detected_attacks
    }
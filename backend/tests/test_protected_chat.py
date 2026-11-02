from fastapi.testclient import TestClient

import app.main as main_module


client = TestClient(main_module.app)


def test_blocked_prompt_does_not_call_llm(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "detect_transformer",
        lambda prompt: {"attack_detected": True},
    )

    calls = []

    def fake_generate(prompt):
        calls.append(prompt)
        return "This should not be called."

    monkeypatch.setattr(
        main_module,
        "generate_response",
        fake_generate,
    )

    response = client.post(
        "/chat/protected",
        json={"prompt": "Example suspicious prompt"},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "BLOCK"
    assert response.json()["llm_response"] is None
    assert calls == []


def test_allowed_prompt_calls_llm(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "detect_transformer",
        lambda prompt: {"attack_detected": False},
    )

    calls = []

    def fake_generate(prompt):
        calls.append(prompt)
        return "Example LLM response"

    monkeypatch.setattr(
        main_module,
        "generate_response",
        fake_generate,
    )

    response = client.post(
        "/chat/protected",
        json={"prompt": "Example benign prompt"},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"
    assert response.json()["llm_response"] == "Example LLM response"
    assert calls == ["Example benign prompt"]
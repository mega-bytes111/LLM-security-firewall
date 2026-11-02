import httpx


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:1b"


def generate_response(prompt: str) -> str:
    """
    Send a prompt to the local Ollama model and return its response.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    # First inference can take longer because the model may need to load.
    response = httpx.post(
        OLLAMA_URL,
        json=payload,
        timeout=120.0,
    )

    response.raise_for_status()

    data = response.json()
    generated_text = data.get("response")

    if not isinstance(generated_text, str):
        raise ValueError(
            "Ollama returned an unexpected response format."
        )

    return generated_text
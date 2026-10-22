import re
import unicodedata


def preprocess_prompt(prompt: str) -> str:
    """
    Normalize input text for rule-based detection.
    """

    # Unicode normalization
    prompt = unicodedata.normalize("NFKC", prompt)

    # Convert to lowercase
    prompt = prompt.lower()

    # Normalize whitespace
    prompt = re.sub(r"\s+", " ", prompt)

    # Remove leading/trailing spaces
    prompt = prompt.strip()

    return prompt
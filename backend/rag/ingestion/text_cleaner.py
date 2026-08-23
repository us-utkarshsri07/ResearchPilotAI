import re


def clean_text(text: str) -> str:
    # Normalize multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text
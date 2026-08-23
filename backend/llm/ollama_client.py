import re
import requests

from backend.core.config import (
    LLM_MODEL,
    OLLAMA_BASE_URL,
)


class OllamaClient:

    def __init__(
        self,
        model: str = LLM_MODEL,
        base_url: str = OLLAMA_BASE_URL,
    ):
        self.model = model
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
    ) -> str:

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
        }

        response = requests.post(
            url,
            json=payload,
            timeout=1000,
        )

        response.raise_for_status()

        answer = response.json()["response"]


        # Remove complete thinking blocks
        answer = re.sub(
            r"<think>.*?</think>",
            "",
            answer,
            flags=re.DOTALL,
        )

        # If </think> exists, keep only text after it
        # if "</think>" in answer:
        #     answer = answer.split("</think>", 1)[1]
        answer = answer.replace("\\n", "\n")

        return answer.strip()
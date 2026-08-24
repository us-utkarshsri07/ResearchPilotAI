import os

from dotenv import load_dotenv
from google import genai

from backend.core.config import GEMINI_MODEL


load_dotenv()


class GeminiClient:

    def __init__(
        self,
        model: str = GEMINI_MODEL,
    ):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Check your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model


    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return (response.text or "").strip()
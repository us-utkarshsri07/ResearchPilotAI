from backend.llm.gemini_client import OllamaClient


def main():

    llm = OllamaClient()

    prompt = """
Explain multi-head attention in the Transformer.

Give a concise answer in 3 points.
"""

    response = llm.generate(prompt)

    print("\nLLM Response:\n")
    print(response)


if __name__ == "__main__":
    main()
import json
from loguru import logger
from backend.llm_client import GroqClient
import re

class ValidationAgent:
    """
    Проверяет корректность рецептов.
    """

    def __init__(self, llm: GroqClient, model: str):
        self.llm = llm
        self.model = model

    async def validate(self, recipes: list[dict]) -> dict:
        logger.info("ValidationAgent: validating recipes...")

        prompt = (
            "Проверь рецепты на корректность. Ответ строго JSON формата:\n"
            "{"
            "  \"valid\": true/false, "
            "  \"issues\": [\"...\"] "
            "}\n\n"
            f"Рецепты:\n{json.dumps(recipes, ensure_ascii=False)}"
        )

        text = await self.llm.completion(
            prompt=prompt,
            model=self.model,
            temperature=0.0,
            max_tokens=1000
        )

        try:
            clean = re.search(r"\{.*\}", text, flags=re.S).group(0)
            return json.loads(clean)
        except Exception:
            logger.error("ValidationAgent JSON error:\n%s", text)
            raise

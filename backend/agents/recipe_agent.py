import json
from loguru import logger
from backend.llm_client import GroqClient
import re

class RecipeAgent:
    """
    Генерирует рецепты на основе нормализованных ингредиентов.
    """

    def __init__(self, llm: GroqClient, model: str):
        self.llm = llm
        self.model = model

    async def generate_recipes(self, ingredients: list[str]) -> list[dict]:
        logger.info("RecipeAgent: generating recipes...")

        prompt = (
            "Составь 3 рецепта, которые можно приготовить только из следующих ингредиентов:\n"
            f"{', '.join(ingredients)}\n\n"
            "Строгий формат ответа: JSON массив объектов:\n"
            "[{\"title\":..., \"ingredients\": [...], \"steps\": [...]}]"
        )

        text = await self.llm.completion(
            prompt=prompt,
            model=self.model,
            temperature=0.4,
            max_tokens=4096
        )

        try:
            clean = re.search(r"\[.*\]|\{.*\}", text, flags=re.S).group(0)
            return json.loads(clean)
        except Exception:
            logger.error("RecipeAgent JSON error:\n%s", text)
            raise

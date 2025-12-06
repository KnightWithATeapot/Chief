import json
from loguru import logger
from backend.llm_client import GroqClient
import re

class NutritionAgent:
    """
    Добавляет дополнительную информацию о каждом рецепте:
    - калории
    - время приготовления
    - полезность
    """

    def __init__(self, llm: GroqClient, model: str):
        self.llm = llm
        self.model = model

    async def enrich_recipes(self, recipes: list[dict]) -> list[dict]:
        logger.info("NutritionAgent: analyzing recipes...")

        prompt = (
            "Проанализируй следующие рецепты и добавь к каждому объекту поля:\n"
            "- calories (число)\n"
            "- cook_time_minutes (число)\n"
            "- healthiness (короткая строка)\n"
            "- summary (1-2 предложения)\n\n"
            "Верни строго JSON массив с обновлёнными объектами рецептов:\n\n"
            f"{json.dumps(recipes, ensure_ascii=False)}"
        )

        text = await self.llm.completion(
            prompt=prompt,
            model=self.model,
            temperature=0.2,
            max_tokens=4096
        )

        try:
            clean = re.search(r"\[.*\]|\{.*\}", text, flags=re.S).group(0)
            return json.loads(clean)
        except Exception:
            logger.error("NutritionAgent JSON error:\n%s", text)
            raise

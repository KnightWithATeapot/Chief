import json
from loguru import logger
from backend.llm_client import GroqClient
import re


class IngredientAgent:
    """
    Принимает сырые ингредиенты (текст/список) и нормализует их.
    """

    def __init__(self, llm: GroqClient, model: str):
        self.llm = llm
        self.model = model

    async def normalize_ingredients(self, raw_input: str) -> list[str]:
        logger.info("IngredientAgent: normalizing ingredients...")

        prompt = (
            "Нормализуй список ингредиентов. "
            "Верни только JSON массив строк. Никакого текста вне JSON.\n\n"
            f"Входные данные:\n{raw_input}"
        )

        text = await self.llm.completion(
            prompt=prompt,
            model=self.model,
            temperature=0.1
        )

        try:
            # Извлекаем чистый JSON (массив или объект)
            clean = re.search(r"\[.*\]|\{.*\}", text, flags=re.S).group(0)
            return json.loads(clean)
        except Exception:
            logger.error("IngredientAgent JSON error:\n%s", text)
            raise

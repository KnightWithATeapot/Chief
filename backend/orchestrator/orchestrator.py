import asyncio
from loguru import logger
import json

from backend.agents.ingredient_agent import IngredientAgent
from backend.agents.recipe_agent import RecipeAgent
from backend.agents.nutrition_agent import NutritionAgent
from backend.agents.validation_agent import ValidationAgent


async def _maybe_await(obj):
    """Помогает единообразно вызывать sync/async методы."""
    if asyncio.iscoroutine(obj):
        return await obj
    return obj


class Orchestrator:
    """
    Главный управляющий объект системы Chief.
    Запускает весь пайплайн:
    1) нормализация ингредиентов
    2) генерация рецептов
    3) обогащение рецептов
    4) валидация
    """

    def __init__(
        self,
        ingredient_agent: IngredientAgent,
        recipe_agent: RecipeAgent,
        nutrition_agent: NutritionAgent,
        validation_agent: ValidationAgent
    ):
        self.ingredient_agent = ingredient_agent
        self.recipe_agent = recipe_agent
        self.nutrition_agent = nutrition_agent
        self.validation_agent = validation_agent

    async def run(self, raw_input: str) -> dict:
        logger.info("Orchestrator: starting pipeline...")
        logger.info(f"Raw input: {raw_input}")

        # 1) Ingredient normalization
        logger.info("Step 1: Normalizing ingredients...")
        try:
            ingredients = await self.ingredient_agent.normalize_ingredients(raw_input)
            # logger.info(f"Normalized ingredients: {ingredients}")
            logger.debug(json.dumps(ingredients, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.exception("Ingredient normalization failed")
            return {"error": f"Ingredient normalization failed: {e}"}

        # 2) Recipe generation
        logger.info("Step 2: Generating recipes...")
        try:
            recipes = await self.recipe_agent.generate_recipes(ingredients)
            # logger.info(f"Recipes generated: {len(recipes)}")
            logger.debug(json.dumps(recipes, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.exception("Recipe generation failed")
            return {"error": f"Recipe generation failed: {e}"}

        # 3) Nutrition enrichment
        logger.info("Step 3: Enriching recipes with nutrition info...")
        try:
            enriched = await self.nutrition_agent.enrich_recipes(recipes)
            logger.info("Nutrition enrichment completed")
        except Exception as e:
            logger.exception("Recipe enrichment failed")
            return {"error": f"Nutrition enrichment failed: {e}"}

        # 4) Validation
        logger.info("Step 4: Validating recipes...")
        try:
            validation = await self.validation_agent.validate(enriched)
        except Exception as e:
            logger.exception("Validation failed")
            return {"error": f"Validation failed: {e}"}

        logger.info("Orchestrator: pipeline finished successfully.")

        # Final structured output
        return {
            "ingredients": ingredients,
            "recipes": enriched,
            "validation": validation
        }

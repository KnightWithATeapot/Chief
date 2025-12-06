import asyncio
from backend.agents.ingredient_agent import IngredientAgent
from backend.agents.recipe_agent import RecipeAgent
from backend.agents.nutrition_agent import NutritionAgent
from backend.agents.validation_agent import ValidationAgent
from backend.orchestrator.orchestrator import Orchestrator
from backend.llm_client import GroqClient

from APIKey import GROQ_API_KEY


async def main():
    llm = GroqClient(GROQ_API_KEY)
    model = "llama-3.3-70b-versatile"

    orchestrator = Orchestrator(
        ingredient_agent=IngredientAgent(llm, model),
        recipe_agent=RecipeAgent(llm, model),
        nutrition_agent=NutritionAgent(llm, model),
        validation_agent=ValidationAgent(llm, model),
    )

    result = await orchestrator.run("яйцо, помидор, сыр")
    print(result)


asyncio.run(main())

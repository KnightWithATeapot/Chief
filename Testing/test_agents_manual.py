import asyncio
from backend.agents.ingredient_agent import IngredientAgent
from backend.agents.recipe_agent import RecipeAgent
from backend.agents.nutrition_agent import NutritionAgent
from backend.agents.validation_agent import ValidationAgent
from backend.llm_client import GroqClient

from APIKey import GROQ_API_KEY

llm = GroqClient(GROQ_API_KEY)
model = "llama-3.3-70b-versatile"


async def main():
    ingr_agent = IngredientAgent(llm, model)
    rec_agent = RecipeAgent(llm, model)
    nut_agent = NutritionAgent(llm, model)
    val_agent = ValidationAgent(llm, model)

    # 1. IngredientAgent
    print("\n=== IngredientAgent ===")
    ingr = await ingr_agent.normalize_ingredients("яйцо, макароны, сыр")
    print(ingr)

    # 2. RecipeAgent
    print("\n=== RecipeAgent ===")
    recipes = await rec_agent.generate_recipes(ingr)
    print(recipes)

    # 3. NutritionAgent
    print("\n=== NutritionAgent ===")
    enriched = await nut_agent.enrich_recipes(recipes)
    print(enriched)

    # 4. ValidationAgent
    print("\n=== ValidationAgent ===")
    validation = await val_agent.validate(enriched)
    print(validation)


asyncio.run(main())

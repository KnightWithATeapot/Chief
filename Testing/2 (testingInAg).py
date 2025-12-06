from APIKey import GROQ_API_KEY
from backend.llm_client import GroqClient
from backend.agents.ingredient_agent import IngredientAgent

llm = GroqClient(api_key=GROQ_API_KEY)
agent = IngredientAgent(llm)

result = agent.normalize("сырок, картоха, мАкАронЫ, масло слив.")
print(result)

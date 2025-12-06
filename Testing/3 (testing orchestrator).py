from APIKey import GROQ_API_KEY
from backend.llm_client import GroqClient
from backend.orchestrator.orchestrator import Orchestrator

llm = GroqClient(api_key=GROQ_API_KEY)
orch = Orchestrator(llm_client=llm)

result = orch.run("яйца, сыр, помидоры", prefs={"vegan": False}, max_recipes=5)
# result уже содержит normalized_ingredients, recipes (каждый с nutrition + validation + score)

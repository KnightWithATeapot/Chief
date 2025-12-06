import asyncio
from backend.orchestrator.orchestrator import Orchestrator
from backend.llm_client import GroqClient

from APIKey import GROQ_API_KEY


async def test():
    llm = GroqClient(api_key=GROQ_API_KEY)

    orchestrator = Orchestrator(llm_client=llm)

    result = await orchestrator.run_async(["картошка", "лук", "яйца"])
    print("RESULT:\n", result)


asyncio.run(test())

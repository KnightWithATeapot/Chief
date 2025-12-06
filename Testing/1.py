from APIKey import GROQ_API_KEY
from backend.llm_client import GroqClient

client = GroqClient(GROQ_API_KEY)

answer = client.chat([
    {"role": "user", "content": "Привет! Скажи, что ты работаешь."}
])

print(answer)

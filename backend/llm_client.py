import httpx
from typing import List, Dict, Optional


class GroqClient:
    """
    Асинхронный клиент для работы с Groq API.
    Используется всеми LLM-агентами проекта.
    """

    def __init__(
        self,
        api_key: str,
        default_model: str = "llama-3.3-70b-versatile"
    ):
        self.api_key = api_key
        self.default_model = default_model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=40.0
        )

    async def completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
    ) -> str:

        model = model or self.default_model

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = await self._client.post(self.api_url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.text}")

        data = response.json()

        text = data["choices"][0]["message"]["content"]

        # удаляем блоки с рассуждениями, если они есть
        if "<think>" in text:
            try:
                text = text.split("</think>")[-1].strip()
            except:
                pass

        return text

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:

        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = await self._client.post(self.api_url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def close(self):
        """Корректное закрытие httpx клиента"""
        await self._client.aclose()

from __future__ import annotations
import os, httpx
from typing import Any, Dict, List

class AzureOpenAIClient:
    def __init__(self):
        self.endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
        self.deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01")
        if not self.endpoint or not self.api_key or not self.deployment:
            raise RuntimeError("Missing AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY / AZURE_OPENAI_DEPLOYMENT")

    async def chat_completions(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 900) -> Dict[str, Any]:
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
        params = {"api-version": self.api_version}
        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        payload = {"messages": messages, "temperature": temperature, "max_tokens": max_tokens}

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, params=params, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx


class MetaLlamaProvider:
    """
    Minimal provider targeting an OpenAI-compatible /v1/chat/completions endpoint.

    Env:
      - OPENAI_COMPAT_BASE_URL: e.g., http://localhost:8000 or https://llama-gateway.example.com
      - OPENAI_COMPAT_API_KEY:  API key if required (Bearer)

    Example:
      provider = MetaLlamaProvider(model="meta-llama-3-8b-instruct")
      text = provider.generate(
          messages=[{"role": "system", "content": "You are a careful medical AI."},
                    {"role": "user", "content": "Summarize this note..."}],
          temperature=0.2, max_tokens=512
      )
    """

    def __init__(
        self,
        model: str = "meta-llama-3-8b-instruct",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_s: float = 60.0,
    ) -> None:
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_COMPAT_BASE_URL", "").rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_COMPAT_API_KEY", "")
        if not self.base_url:
            raise RuntimeError(
                "OPENAI_COMPAT_BASE_URL not configured; "
                "set env or pass base_url to MetaLlamaProvider()."
            )
        self._client = httpx.Client(timeout=timeout_s)

    def generate(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
        top_p: float = 0.95,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Return assistant text from a chat completion."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        if extra:
            payload.update(extra)

        url = f"{self.base_url}/v1/chat/completions"
        resp = self._client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        # OpenAI-format compatibility
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            # vLLM older variants may use slightly different key names; fallback
            if isinstance(data, dict):
                choice = data.get("choices", [{}])[0]
                msg = choice.get("message") or {}
                return msg.get("content") or choice.get("text", "")
            return ""

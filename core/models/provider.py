from __future__ import annotations
import json, re
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config.settings import settings
try:
    import openai
except Exception:
    openai = None
try:
    import anthropic
except Exception:
    anthropic = None
def _strip_code_fences(text: str) -> str:
    if text is None: return ""
    return re.sub(r"```[a-zA-Z]*\n?|```", "", text).strip()
def coerce_json(text: str) -> dict | list:
    t = _strip_code_fences(text)
    try:
        return json.loads(t)
    except Exception:
        return {"findings": [], "notes": t[:500]}
class BaseProvider:
    def chat(self, system: str, prompt: str) -> str: raise NotImplementedError
class OpenAIProvider(BaseProvider):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def chat(self, system: str, prompt: str) -> str:
        if not settings.openai_api_key or openai is None: raise RuntimeError("OpenAI not configured")
        client = openai.OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
class AnthropicProvider(BaseProvider):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def chat(self, system: str, prompt: str) -> str:
        if not settings.anthropic_api_key or anthropic is None: raise RuntimeError("Anthropic not configured")
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(model="claude-3-haiku-20240307", system=system, max_tokens=512, messages=[{"role":"user","content":prompt}])
        return "".join(getattr(b, "text", "") for b in msg.content)
class LocalFallbackProvider(BaseProvider):
    def chat(self, system: str, prompt: str) -> str:
        return json.dumps({"findings": [], "notes": "local-fallback: " + prompt[:200]})
class ModelRunner:
    def __init__(self): self.providers = [OpenAIProvider(), AnthropicProvider(), LocalFallbackProvider()]
    def chat_json(self, system: str, prompt: str) -> dict | list:
        last_err = None
        for p in self.providers:
            try:
                out = p.chat(system, prompt)
                return coerce_json(out)
            except Exception as e:
                last_err = e; continue
        return {"findings": [], "notes": f"provider error: {last_err}"}

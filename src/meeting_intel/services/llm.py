import json
from typing import Any

from meeting_intel.core.config import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = None
        if not settings.offline_mode and settings.openai_api_key:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def production_enabled(self) -> bool:
        return self.client is not None

    async def complete_json(self, system: str, user: str, schema_hint: str) -> dict[str, Any]:
        if self.client is None:
            return self._offline_response(user)

        response = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"{user}\n\nReturn JSON matching: {schema_hint}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def answer(self, system: str, user: str) -> str:
        if self.client is None:
            context = user.split("Context:", 1)[-1].strip() if "Context:" in user else user
            preview = " ".join(context.split())[:300]
            return f"Offline answer based on retrieved context: {preview}"
        response = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def _offline_response(self, user: str) -> dict[str, Any]:
        lines = [line.strip() for line in user.splitlines() if line.strip()]
        preview = " ".join(lines)[:280]
        return {
            "summary": f"Offline summary: {preview}",
            "action_items": [],
            "decisions": [],
            "risks": [],
            "follow_ups": [],
        }

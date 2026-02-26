import httpx

from app.core.config import settings


class OpenAIService:
    base_url = 'https://api.openai.com/v1/responses'

    async def summarize(self, content: str) -> str:
        if not settings.openai_api_key:
            return f'[MOCK SUMMARY] {content[:120]}'

        payload = {'model': 'gpt-4.1-mini', 'input': f'請整理以下內容並給出重點摘要:\n{content}'}
        headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(self.base_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get('output', [{}])[0].get('content', [{}])[0].get('text', '') or 'No summary'

import httpx

from app.core.config import settings


async def summarize_message(content: str) -> str:
    if not settings.openai_api_key:
        return f'[Mock AI] Summary: {content[:100]}'

    headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
    payload = {
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': 'Summarize business messages into concise action items.'},
            {'role': 'user', 'content': content},
        ],
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

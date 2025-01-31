import asyncio
from openai import AsyncOpenAI
from src.settings import OPENROUTER_API_KEY, MAX_TOKENS

async def chat_with_model_async(messages: list[dict], model_name: str, max_tokens: int = MAX_TOKENS) -> str:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    completion = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens
    )

    return completion.choices[0].message.content
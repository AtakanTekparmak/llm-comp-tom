import asyncio
from openai import AsyncOpenAI
from src.settings import OPENROUTER_API_KEY, MAX_TOKENS, VERBOSE

async def chat_with_model_async(messages: list[dict], model_name: str, max_tokens: int = MAX_TOKENS, max_retries: int = 3) -> str:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    for attempt in range(max_retries):
        try:
            completion = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens
            )
            
            if completion and completion.choices:
                return completion.choices[0].message.content
            else:
                if VERBOSE:
                    print(f"Warning: Empty response from model on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return "Error: No response from model"
                await asyncio.sleep(1)  # Wait before retry
                
        except Exception as e:
            if VERBOSE:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return f"Error: {str(e)}"
            await asyncio.sleep(1)  # Wait before retry
    
    return "Error: Max retries exceeded"
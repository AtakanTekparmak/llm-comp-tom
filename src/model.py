import asyncio
from openai import AsyncOpenAI
from src.settings import OPENROUTER_API_KEY, MAX_TOKENS, VERBOSE

async def chat_with_model_async(messages: list[dict], model_name: str, model_api_name: str, max_tokens: int = MAX_TOKENS, max_retries: int = 3) -> str:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    for attempt in range(max_retries):
        try:
            if VERBOSE:
                print(f"Attempting API call to {model_name} (attempt {attempt + 1}/{max_retries})")
            
            completion = await client.chat.completions.create(
                model=model_api_name,
                messages=messages,
                max_tokens=max_tokens,
                timeout=30  # Add timeout
            )
            
            if completion and completion.choices:
                response = completion.choices[0].message.content
                if VERBOSE:
                    print(f"Successful response from {model_name}")
                return response
            else:
                error_msg = f"Empty response from model {model_name} on attempt {attempt + 1}"
                if VERBOSE:
                    print(error_msg)
                if attempt == max_retries - 1:
                    return f"Error: {error_msg}"
                await asyncio.sleep(1)  # Shorter delay between retries
                
        except Exception as e:
            error_msg = f"API error with {model_name} on attempt {attempt + 1}: {str(e)}"
            if VERBOSE:
                print(error_msg)
            if attempt == max_retries - 1:
                return f"Error: {error_msg}"
            await asyncio.sleep(1)  # Shorter delay between retries
    
    return f"Error: Max retries exceeded for {model_name}"
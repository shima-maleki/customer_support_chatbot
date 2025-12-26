from typing import AsyncGenerator

from openai import AsyncOpenAI

from assistant.config import settings


async def get_streaming_response(
    messages: str,
    user_id: str,
    model: str = "gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    """
    Minimal async streaming response generator using OpenAI Chat Completions.

    Args:
        messages: User message or prompt text.
        user_id: Identifier for the user session (passed through for tracing).
        model: OpenAI chat model to use.
    Yields:
        Incremental chunks of the assistant's response as strings.
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    stream = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful retail support assistant."},
            {"role": "user", "content": messages},
        ],
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content

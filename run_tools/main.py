import asyncio
import json
from functools import wraps
from typing import AsyncGenerator

import click
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from assistant.application.generate_response import get_streaming_response


# ---------- FastAPI app (for Streamlit UI) ----------
app = FastAPI(title="Customer Support Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _send_stream(websocket: WebSocket, user_id: str, message: str) -> None:
    """Stream chunks back to the websocket client."""
    async for chunk in get_streaming_response(messages=message, user_id=user_id):
        await websocket.send_json({"chunk": chunk})
    await websocket.send_json({"response": "done"})


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        user_id = data.get("user_id", "anonymous")
        message = data.get("message", "")
        if not message:
            await websocket.send_json({"error": "message is required"})
            return
        await _send_stream(websocket, user_id, message)
    except WebSocketDisconnect:
        return
    except Exception as e:
        await websocket.send_json({"error": str(e)})


# ---------- CLI helper for quick calls ----------
def async_command(f):
    """Decorator to run an async click command."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.option(
    "--user-id",
    type=str,
    required=True,
    help="ID of the User.",
)
@click.option(
    "--query",
    type=str,
    required=True,
    help="Query to call the agent with.",
)
@async_command
async def main(user_id: str, query: str) -> None:
    """CLI command to stream a response from the assistant."""
    async for chunk in get_streaming_response(
        messages=query,
        user_id=user_id,
    ):
        print(f"\033[32m{chunk}\033[0m", end="", flush=True)


if __name__ == "__main__":
    main()

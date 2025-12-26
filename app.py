import streamlit as st
import asyncio
import websockets
import json

FASTAPI_WS_URL = "ws://localhost:8000/ws/chat"

st.set_page_config(page_title="Retail AI Assistant", layout="centered")
st.title("🧠 Retail AI Assistant")
st.markdown("Talk to your assistant using the input below.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_id = st.text_input("Please Enter Your Name", value="user_name")
message = st.chat_input("How can I help you today?")

async def stream_chat(user_id, message):
    async with websockets.connect(FASTAPI_WS_URL) as websocket:
        await websocket.send(json.dumps({"user_id": user_id, "message": message}))

        full_response = ""
        while True:
            try:
                response = await websocket.recv()
                response_data = json.loads(response)

                if "chunk" in response_data:
                    yield response_data["chunk"]

                elif "response" in response_data:
                    break

                elif "error" in response_data:
                    yield f"[ERROR]: {response_data['error']}"
                    break
            except websockets.ConnectionClosed:
                break

def run_streaming(user_id, message):
    response_chunks = []

    async def collect_chunks():
        async for chunk in stream_chat(user_id, message):
            response_chunks.append(chunk)
            response_container.markdown("**Assistant:** " + "".join(response_chunks))

    asyncio.run(collect_chunks())
    return "".join(response_chunks)

if message:
    st.session_state.chat_history.append(("You", message))
    response_container = st.empty()
    full_response = run_streaming(user_id, message)
    st.session_state.chat_history.append(("Assistant", full_response))

# Display chat history
st.divider()
st.subheader("💬 Conversation History")
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")

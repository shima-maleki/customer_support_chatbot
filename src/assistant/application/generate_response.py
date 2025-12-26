import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src/")))

import uuid
from typing import Any, AsyncGenerator, Union
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from opik.integrations.langchain import OpikTracer
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from assistant.application.agents.graph import create_workflow_graph 
from assistant.application.agents.state import CustomerSupportAgentState
from assistant.config import settings


async def get_response(
    messages: str | list[str] | list[dict[str, Any]],
    user_id: str,
    new_thread: bool = False,
) -> tuple:
    """Run a conversation through the workflow graph.

    Args:
        message: Initial message to start the conversation.
        user_id: Unique identifier.

    Returns:
            - The final state after running the workflow.

    Raises:
        RuntimeError: If there's an error running the conversation workflow.
    """

    graph_builder = create_workflow_graph()

    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.MONGO_DB_NAME,
            checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            opik_tracer = OpikTracer(graph=graph.get_graph(xray=True))

            thread_id = (
                user_id if not new_thread else f"{user_id}-{uuid.uuid4()}"
            )
            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [opik_tracer],
            }
            output_state = await graph.ainvoke(
                input={
                    "customer_query": __format_messages(messages=messages),
                },
                config=config,
            )
        last_message = output_state["final_response"]
        print(last_message)
        retrieved_content = output_state.get("retrieved_content", "Don't worry someone from our on-call team will be reaching out to your shortly at your number for assistance immediately!")
        return last_message, retrieved_content
    except Exception as e:
        raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e



async def get_streaming_response(
    messages: str | list[str] | list[dict[str, Any]],
    user_id: str,
    new_thread: bool = False,
) -> AsyncGenerator[str, None]:
    """Run a conversation through the workflow graph with streaming response.

    Args:
        messages: Initial message to start the conversation.
        user_id: Unique identifier.
        new_thread: Whether to create a new conversation thread.

    Yields:
        Chunks of the response as they become available.

    Raises:
        RuntimeError: If there's an error running the conversation workflow.
    """
    graph_builder = create_workflow_graph()

    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.MONGO_DB_NAME,
            checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            opik_tracer = OpikTracer(graph=graph.get_graph(xray=True))

            thread_id = (
                user_id if not new_thread else f"{user_id}-{uuid.uuid4()}"
            )
            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [opik_tracer],
            }

            async for chunk in graph.astream(
                input={
                    "customer_query": __format_messages(messages=messages),
                },
                config=config,
                stream_mode="messages",
            ):
                if chunk[1]["langgraph_node"] == "generate_department_response" and isinstance(
                    chunk[0], AIMessageChunk
                ):
                    yield chunk[0].content

                if chunk[1]["langgraph_node"] == "escalate_to_oncall_team" and isinstance(
                    chunk[0], AIMessageChunk
                ):
                    yield chunk[0].content

    except Exception as e:
        raise RuntimeError(
            f"Error running streaming conversation workflow: {str(e)}"
        ) from e


def __format_messages(
    messages: Union[str, list[dict[str, Any]]],
) -> list[Union[HumanMessage, AIMessage]]:
    """Convert various message formats to a list of LangChain message objects.

    Args:
        messages: Can be one of:
            - A single string message
            - A list of string messages
            - A list of dictionaries with 'role' and 'content' keys

    Returns:
        List[Union[HumanMessage, AIMessage]]: A list of LangChain message objects
    """

    if isinstance(messages, str):
        return [HumanMessage(content=messages)]

    if isinstance(messages, list):
        if not messages:
            return []

        if (
            isinstance(messages[0], dict)
            and "role" in messages[0]
            and "content" in messages[0]
        ):
            result = []
            for msg in messages:
                if msg["role"] == "user":
                    result.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    result.append(AIMessage(content=msg["content"]))
            return result

        return [HumanMessage(content=message) for message in messages]

    return []
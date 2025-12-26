from functools import lru_cache
from langgraph.graph import StateGraph, END
from assistant.application.agents.state import CustomerSupportAgentState
from assistant.application.agents.nodes import (
    categorize_inquiry,
    generate_department_response,
    analyze_inquiry_sentiment,
    accept_user_input_oncall,
    escalate_to_oncall_team
)
from assistant.application.agents.edges import determine_route


@lru_cache(maxsize=1)
def create_workflow_graph():
    # Create a typed LangGraph state graph using the custom CustomerSupportAgentState
    customer_support_graph = StateGraph(CustomerSupportAgentState)

    # Register each functional node in the graph that represents a step in the agent workflow

    # Step 1: Categorize the incoming query by department (e.g., billing, records, etc.)
    customer_support_graph.add_node("categorize_inquiry", categorize_inquiry)
    # Step 2: Analyze the user's sentiment (positive, neutral, negative, distress)
    customer_support_graph.add_node("analyze_inquiry_sentiment", analyze_inquiry_sentiment)

    # Step 4a: Accept user input for escalation to emergency on-call team (for distress sentiment)
    customer_support_graph.add_node("accept_user_input_oncall", accept_user_input_oncall)
    # Step 4b: Escalate to on-call emergency doctor team using submitted details
    customer_support_graph.add_node("escalate_to_oncall_team", escalate_to_oncall_team)

    # Step 5: Generate a department-specific response using RAG if sentiment is positive or neutral
    customer_support_graph.add_node("generate_department_response", generate_department_response)

    # Define the flow of transitions between the nodes in the graph
    # After categorizing the query, move to sentiment analysis
    customer_support_graph.add_edge("categorize_inquiry", "analyze_inquiry_sentiment")
    # After sentiment analysis, use conditional routing to determine next steps
    customer_support_graph.add_conditional_edges(
        "analyze_inquiry_sentiment",
        determine_route,
        [
            "accept_user_input_oncall",
            "generate_department_response",
        ]
    )

    # If the user input is collected for on-call emergency, route to on-call team
    customer_support_graph.add_edge("accept_user_input_oncall", "escalate_to_oncall_team")
    customer_support_graph.add_edge("escalate_to_oncall_team", END)

    # If sentiment is neutral or positive, generate a department response and finish
    customer_support_graph.add_edge("generate_department_response", END)

    # Set the starting point of the workflow
    customer_support_graph.set_entry_point("categorize_inquiry")
    return customer_support_graph

  # Compile the graph
# compiled_support_agent = create_workflow_graph().compile()
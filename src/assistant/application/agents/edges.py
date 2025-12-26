from assistant.application.agents.state import CustomerSupportAgentState

# Define the router function that directs the flow based on sentiment and category
def determine_route(support_state: CustomerSupportAgentState) -> str:

    # Determine the next node based on query sentiment and category.
    # - For all query categories (including GENERAL), generate appropriate responses
    # - Only escalate to on-call team in extreme distress cases (not implemented in this version)
    # - For negative sentiment, still try to provide a helpful response

    query_category = support_state.get("query_category", "GENERAL")
    query_sentiment = support_state.get("query_sentiment", "Neutral")

    # Always route to generate_department_response - it handles both RAG and conversational responses
    # based on the category (GENERAL vs specific departments)
    return "generate_department_response"
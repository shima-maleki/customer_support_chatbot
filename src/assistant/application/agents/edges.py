from assistant.application.agents.state import CustomerSupportAgentState

# Define the router function that directs the flow based on sentiment and category
def determine_route(support_state: CustomerSupportAgentState) -> str:

    # Determine the next node based on query sentiment and category.
    # - Escalate to human support agent if sentiment is negative i.e fill form for escalation
    # - Escalate to emergency on-call team if sentiment is distress i.e fill form for on-call doctors
    # - Otherwise, use department-specific RAG response

    if support_state["query_sentiment"] == "Negative":
        return "accept_user_input_oncall"
    elif (support_state["query_sentiment"] in ["Neutral", "Positive"]) and (support_state["query_category"] in ['HR', 'IT_SUPPORT', 'FACILITY_AND_ADMIN', 'BILLING_AND_PAYMENT', 'SHIPPING_AND_DELIVERY']):
        return "generate_department_response"
    else:
        return "accept_user_input_oncall"
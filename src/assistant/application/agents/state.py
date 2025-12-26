from typing import TypedDict, Literal
from pydantic import BaseModel

class CustomerSupportAgentState(TypedDict):
    customer_query: str
    query_category: str
    query_sentiment: str
    escalation_cust_info: dict
    oncall_cust_info: dict
    final_response: str
    retrieved_content: str

class QueryCategory(BaseModel):
    categorized_topic: Literal['HR', 'IT_SUPPORT', 'FACILITY_AND_ADMIN', 'BILLING_AND_PAYMENT', 'SHIPPING_AND_DELIVERY']

class QuerySentiment(BaseModel):
    sentiment: Literal['Positive', 'Neutral', 'Negative']


def state_to_str(state: CustomerSupportAgentState) -> str:
    if "final_response" in state and bool(state["final_response"]):
        conversation = state["final_response"]
    else:
        conversation = ""


    return f"""
            conversation={conversation})
            """
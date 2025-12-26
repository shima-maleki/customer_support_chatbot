import os
from typing import Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from assistant.infrastructure.qdrant.service import vectorstore
from langchain_core.messages import AIMessage, HumanMessage
from assistant.application.agents.state import CustomerSupportAgentState, QueryCategory, QuerySentiment
from assistant.domain.prompts import (
    SENTIMENT_CATEGORY_PROMPT,
    RESPONSE_PROMPT,
    ROUTE_CATEGORY_PROMPT,
)

load_dotenv()

vector_store = vectorstore()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, stream_usage=True)

def categorize_inquiry(support_state: CustomerSupportAgentState) -> CustomerSupportAgentState:
    """
    Classify the customer query into 'Billing', 'Appointments', 'Records' or 'Insurance'.
    """

    query = support_state["customer_query"]

    route_category_prompt = ROUTE_CATEGORY_PROMPT.prompt

    prompt = route_category_prompt.format(customer_query=query)
    route_category = llm.with_structured_output(QueryCategory).invoke(prompt)

    return {
        "query_category": route_category.categorized_topic
    }



def generate_department_response(support_state: CustomerSupportAgentState) -> CustomerSupportAgentState:
    """
    Provide a department support response by combining knowledge from the vector store and LLM.
    """
    # Retrieve category and ensure it is lowercase for metadata filtering
    categorized_topic = support_state["query_category"]
    query = support_state["customer_query"][0].content

    # Use metadata filter for department - specific queries
    if categorized_topic == ['HR', 'IT_SUPPORT', 'FACILITY_AND_ADMIN', 'BILLING_AND_PAYMENT', 'SHIPPING_AND_DELIVERY']:
        metadata_filter = {"source": categorized_topic.lower()}
        department = categorized_topic
    else:
        metadata_filter = None


    # Perform retrieval from VectorDB
    relevant_docs = vector_store.similarity_search(
                            query=query,
                            k=3,
                            filters=metadata_filter
                        )
    retrieved_content = "\n\n".join(doc.page_content for doc in relevant_docs)

    # Combine retrieved information into the prompt
    response_prompt = RESPONSE_PROMPT.prompt

    # Generate the final response using the LLM
    chain = response_prompt | llm
    reply = chain.invoke({
        "customer_query": query,
        "retrieved_content": retrieved_content
    }).content

    # Update and return the modified support state
    return {
        "final_response": reply, "retrieved_content": retrieved_content
    }

def analyze_inquiry_sentiment(support_state: CustomerSupportAgentState) -> CustomerSupportAgentState:
    """
    Analyze the sentiment of the customer query as Positive, Neutral, Negative or Distress.
    """

    query = support_state["customer_query"]
    sentiment_category_prompt = SENTIMENT_CATEGORY_PROMPT.prompt
    prompt = sentiment_category_prompt.format(customer_query=query)
    sentiment_category = llm.with_structured_output(QuerySentiment).invoke(prompt)

    return {
        "query_sentiment": sentiment_category.sentiment
    }


def accept_user_input_oncall(support_state: CustomerSupportAgentState) -> CustomerSupportAgentState:

    # REMEMBER: You can always customize the way you accept user input by modifying the code below
    # here we use jupyter widgets so you don't have to install too many external dependencies

    user_name = input('Please enter your name: ')
    user_phone_number = input('Please enter your number: ')

    while not user_name and user_phone_number:
        user_name = input('Please enter your name: ')
        user_phone_number = input('Please enter your number: ')

    result = HumanMessage(content = f"{user_name} {user_phone_number}")

    # Return updated agent state with emergency form details
    return {
        'oncall_cust_info': result
    }


def escalate_to_oncall_team(support_state: CustomerSupportAgentState) -> CustomerSupportAgentState:

    # REMEMBER: You can always customize the way you notify the emergency on-call medical team of doctors by adding custom code below.
    # This could include paging them, sending them notifications using specific platform APIs like whatsapp etc.
    # Here we have kept it very simple:
    #  we just show a response back to the user showing the details they entered in the form earlier
    #  and telling them they will be contacted by a doctor from the on-call team

    # get the customer info from agent state which they entered in the form
    oncall_cust_info = support_state['oncall_cust_info'].content
    # the following response will be shown to the user and can also be sent (customer form inputs) to your on-call doctors
    response = AIMessage(content = "Don't worry " + oncall_cust_info.split()[0] +
               "!, someone from our on-call team will be reaching out to your shortly at " +
                oncall_cust_info.split()[1] +
                " for assistance immediately!")

    # NOTE: You can always add custom code here to call specific APIs like whatsapp to notify your on-call doctors

    return {
        "final_response": response
    }
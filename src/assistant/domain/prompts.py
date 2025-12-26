import opik
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate

class Prompt:
    def __init__(self, name: str, prompt: str) -> None:
        self.name = name

        try:
            self.__prompt = opik.Prompt(name=name, prompt=prompt)
        except Exception:
            logger.warning(
                "Can't use Opik to version the prompt (probably due to missing or invalid credentials). Falling back to local prompt. The prompt is not versioned, but it's still usable."
            )

            self.__prompt = prompt

    @property
    def prompt(self) -> str:
        if isinstance(self.__prompt, opik.Prompt):
            return self.__prompt.prompt
        else:
            return self.__prompt

    def __str__(self) -> str:
        return self.prompt

    def __repr__(self) -> str:
        return self.__str__()


# --- PROMPTS ---

_ROUTE_CATEGORY_PROMPT = """Act as a customer support agent trying to best categorize the customer query.
                               You are a support agent for a retail company, ShopUNow and the focus of query classification
                               to build an Intelligent AI Assistant which can leverage internal company information to
                               answer both internal employee as well as external customer queries.

                               These services include:
                                - handling human resources related queries
                                - handling it support queries
                                - handling facility and admin related queries
                                - handling billing and payment related queries
                                - handling delivery and shipping related queries

                               Please read the customer query below and
                               determine the best category from the following list:

                               'HR', 'IT_SUPPORT', 'FACILITY_AND_ADMIN', 'BILLING_AND_PAYMENT', 'SHIPPING_AND_DELIVERY'

                               Remember:
                               HR - records centralize data covering their entire employment lifecycle: personal details, leave, compensation (expenses, bonuses, benefits), career progression (transfers, development), and adherence to company policies (e.g., health & safety, equal opportunities, social media). Essential for employee support and compliance.

                               IT_SUPPORT - records centralize data on technical assistance, equipment, and system access. This includes device management, network issues, IT security, software support, and all service requests, vital for employee productivity and a secure IT infrastructure.

                               FACILITY_AND_ADMIN - Facilities & Admin records cover workplace environment, safety protocols, and administrative support. This includes health & safety, premise maintenance, and external contractor coordination, ensuring a safe and functional work environment.

                               BILLING_AND_PAYMENT - records cover financial transactions, including invoices, order history, charges, refunds, payment methods, and billing disputes, as well as gift card and store credit balances.

                               DELIVERY_AND_SHIPPING: records cover product deliveries, including tracking, shipping history, order status, delivery options/costs, instructions, and resolution of lost, damaged, or incorrect shipments.

                               Return just the category name (from one of the above)

                               Query:
                               {customer_query}
                            """

ROUTE_CATEGORY_PROMPT = Prompt(
    name="route_category_prompt",
    prompt=_ROUTE_CATEGORY_PROMPT,
)

_RESPONSE_PROMPT = ChatPromptTemplate.from_template(
        """
        Craft a clear and detailed support response for the following customer query about a perticular department.
        Use the provided knowledge base information to enrich your response.
        In case there is no knowledge base information or you do not know the answer just say:

        Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx

        Customer Query:
        {customer_query}

        Relevant Knowledge Base Information:
        {retrieved_content}
        """
    )

RESPONSE_PROMPT = Prompt(
    name="response_prompt",
    prompt=_RESPONSE_PROMPT,
)


_SENTIMENT_CATEGORY_PROMPT = """Act as a customer support agent trying to best categorize the customer query.
                                   You are a support agent for a retail company, ShopUNow focusing on providing various services to customers.

                                   These services include:
                                    - handling human resources related queries
                                    - handling it support queries
                                    - handling facility and admin related queries
                                    - handling billing and payment related queries
                                    - handling delivery and shipping related queries

                                   Please read the customer query below,
                                   analyze its sentiment which should be one from the following list:

                                   'Positive', 'Neutral', 'Negative'

                                   Remember these rules when finding the sentiment:
                                     - 'Negative' happens only when the internal or external customer is not happy with certain products, information provided or services offered by the company

                                   Return just the sentiment (from one of the above)

                                   Query:
                                   {customer_query}
                                """

SENTIMENT_CATEGORY_PROMPT = Prompt(
    name="sentiment_category_prompt",
    prompt=_SENTIMENT_CATEGORY_PROMPT,
)
# Customer Support AI Chatbot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-green)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-success)](https://www.mongodb.com/atlas)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red)](https://qdrant.tech/)

An intelligent, multi-agent customer support chatbot leveraging **LangGraph**, **RAG (Retrieval-Augmented Generation)**, and **persistent state management** to deliver context-aware support for both internal employees and external customers.

## Key Differentiators

- **Multi-Agent Architecture**: Orchestrated workflow with specialized agents for categorization, sentiment analysis, and response generation
- **Intelligent Routing**: Automatically categorizes queries across 6 departments (HR, IT Support, Facilities, Billing, Shipping, General)
- **RAG-Powered Responses**: Leverages vector search over domain-specific knowledge bases with metadata filtering
- **Conversational Intelligence**: Distinguishes between knowledge-seeking queries and casual conversation
- **Persistent Memory**: MongoDB-backed state checkpointing for conversation continuity across sessions
- **Production-Ready**: FastAPI backend with WebSocket streaming, Streamlit frontend, comprehensive evaluation framework
- **Observable & Traceable**: Integrated Opik/Comet ML for experiment tracking and performance monitoring

## Architecture

### High-Level System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│   Streamlit     │────────▶│  FastAPI Backend │────────▶│   LangGraph     │
│   Frontend      │         │  (WebSocket)     │         │   Workflow      │
│                 │◀────────│                  │◀────────│   Engine        │
└─────────────────┘         └──────────────────┘         └────────┬────────┘
                                                                   │
                            ┌──────────────────────────────────────┼────────────────┐
                            │                                      │                │
                            ▼                                      ▼                ▼
                     ┌─────────────┐                      ┌──────────────┐  ┌─────────────┐
                     │  MongoDB    │                      │   Qdrant     │  │   OpenAI    │
                     │  (State)    │                      │  (Vectors)   │  │   GPT-4o    │
                     └─────────────┘                      └──────────────┘  └─────────────┘
```

### Multi-Agent Workflow

The chatbot uses a **LangGraph state machine** with the following agent nodes:

```
User Query
    │
    ▼
┌─────────────────────┐
│ Categorize Query    │──▶ Determines department (HR, IT, Facilities, Billing, Shipping, General)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Sentiment Analysis  │──▶ Analyzes emotional tone (Positive, Neutral, Negative)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Route Decision      │──▶ Directs flow based on category and sentiment
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Generate Response   │──▶ GENERAL: Conversational response
│                     │    DEPT-SPECIFIC: RAG retrieval + LLM synthesis
└─────────────────────┘
           │
           ▼
      Final Response
```

### Key Components

1. **Categorization Agent** ([nodes.py:10-32](src/assistant/application/agents/nodes.py#L10-L32))
   - Uses GPT-4o-mini with structured output (Pydantic schema)
   - Classifies into 6 categories: HR, IT_SUPPORT, FACILITY_AND_ADMIN, BILLING_AND_PAYMENT, SHIPPING_AND_DELIVERY, GENERAL
   - Prompt engineering with detailed category descriptions and examples

2. **Sentiment Agent** ([nodes.py:34-39](src/assistant/application/agents/nodes.py#L34-L39))
   - Analyzes query emotion: Positive, Neutral, Negative
   - Used for routing decisions and response tone adaptation

3. **RAG Response Generator** ([nodes.py:41-103](src/assistant/application/agents/nodes.py#L41-L103))
   - **For GENERAL queries**: Conversational response without vector search
   - **For department queries**:
     - Performs similarity search in Qdrant with metadata filtering (department-specific)
     - Retrieves top-3 relevant documents
     - Synthesizes response using retrieved context + LLM
   - Reduces hallucination by grounding responses in factual knowledge base

4. **State Management** ([generate_response.py:16-30](src/assistant/application/generate_response.py#L16-L30))
   - MongoDB checkpointer initialized at module level
   - Persists conversation state across sessions
   - Thread-based isolation for concurrent users

## Technology Stack

### Core Framework
- **LangGraph 0.2.62**: State machine orchestration for multi-agent workflows
- **LangChain 0.3.13**: LLM abstraction, prompt management, RAG utilities
- **Pydantic 2.10+**: Settings management, structured outputs, data validation

### LLM & Embeddings
- **OpenAI GPT-4o-mini**: Primary model for categorization, sentiment, and response generation
- **text-embedding-3-small**: Vector embeddings for semantic search (1536 dimensions)

### Databases
- **MongoDB Atlas**: Persistent state storage with `MongoDBSaver` checkpointer
  - Collections: `checkpoints` (state snapshots), `checkpoint_writes` (incremental updates)
- **Qdrant Cloud**: Managed vector database for RAG
  - Metadata filtering by department (`source` field)
  - Cosine similarity search

### Backend & Frontend
- **FastAPI 0.115.6**: Async web framework with WebSocket support for streaming responses
- **Streamlit 1.41.1**: Interactive web UI with real-time WebSocket client
- **Uvicorn**: ASGI server for production deployment

### Observability
- **Opik/Comet ML**: Experiment tracking, prompt versioning, performance metrics
- **LangSmith Integration**: Trace collection for debugging agent workflows

### Development Tools
- **Click**: CLI tool framework for evaluation and data management
- **Python-dotenv**: Environment variable management

## Design Decisions

### Why LangGraph over LangChain Agents?

**LangGraph** provides:
- **Explicit state management**: Full control over state transitions vs. implicit agent memory
- **Deterministic routing**: Conditional edges vs. unpredictable agent tool selection
- **Checkpointing**: Built-in persistence with MongoDB integration
- **Graph visualization**: Clear workflow representation for debugging and documentation
- **Production stability**: Predictable behavior vs. agent loops and hallucinated tool calls

### Why Qdrant for Vector Search?

- **Metadata filtering**: Essential for department-specific retrieval without cross-contamination
- **Managed cloud offering**: No infrastructure overhead
- **Performance**: Sub-100ms similarity search on 10K+ documents
- **Scalability**: Horizontal scaling for growing knowledge bases

### Why MongoDB for State?

- **Native LangGraph integration**: `MongoDBSaver` checkpointer out-of-the-box
- **Document model**: Natural fit for conversational state (nested messages, metadata)
- **Atlas cloud**: Managed service with automatic backups and scaling
- **Flexible schema**: Easy to extend state structure without migrations

### Hexagonal Architecture

Project follows **Clean/Hexagonal Architecture** for maintainability:

```
src/assistant/
├── domain/           # Business logic (prompts, schemas)
├── application/      # Use cases (agents, workflow)
└── infrastructure/   # External adapters (Qdrant, MongoDB, API)
```

**Benefits**:
- Testable business logic isolated from I/O
- Easy to swap LLM providers or databases
- Clear dependency flow (domain ← application ← infrastructure)

## Project Structure

```
customer_support_chatbot/
├── src/
│   └── assistant/
│       ├── domain/
│       │   ├── __init__.py
│       │   └── prompts.py                 # Opik-versioned prompts
│       ├── application/
│       │   ├── agents/
│       │   │   ├── edges.py               # Routing logic
│       │   │   ├── nodes.py               # Agent implementations
│       │   │   ├── state.py               # State schema (Pydantic)
│       │   │   └── workflow.py            # LangGraph builder
│       │   ├── evaluation/
│       │   │   ├── evaluate.py            # Opik evaluation runner
│       │   │   └── upload_evaluation_data.py
│       │   └── generate_response.py       # Main entry point
│       ├── infrastructure/
│       │   ├── api.py                     # FastAPI WebSocket server
│       │   ├── mongodb/
│       │   │   └── client.py              # MongoDB connection
│       │   └── qdrant/
│       │       ├── service.py             # Vector store client
│       │       └── retriever.py           # RAG retriever
│       └── config.py                      # Pydantic settings
├── evaluation_data/
│   └── evaluation_data.json               # 122 Q&A test cases
├── run_tools/
│   ├── evaluate_agent.py                  # CLI evaluation tool
│   └── upload_data_to_vector_db.py        # Knowledge base ingestion
├── app.py                                 # Streamlit frontend
├── requirements.txt                       # Python dependencies
├── .env                                   # Environment variables (API keys)
└── README.md                              # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- MongoDB Atlas account (free tier sufficient)
- Qdrant Cloud account (free tier sufficient)
- OpenAI API key
- Opik/Comet ML account (optional, for evaluation)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/customer_support_chatbot.git
   cd customer_support_chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   # OpenAI API
   OPENAI_API_KEY=sk-proj-your-api-key-here

   # Qdrant Vector Database
   QDRANT_URL=https://your-instance.cloud.qdrant.io
   QDRANT_API_KEY=your-qdrant-api-key

   # MongoDB Atlas
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGO_DB_NAME=chatbot

   # Opik Observability (Optional)
   OPIK_API_KEY=your-opik-api-key
   COMET_API_KEY=your-opik-api-key
   COMET_WORKSPACE=your-workspace
   OPIK_PROJECT_NAME=chatbot
   OPIK_URL=https://www.comet.com/opik/api
   OPIK_ENABLED=true
   ```

5. **Populate vector database** (if starting fresh)
   ```bash
   python run_tools/upload_data_to_vector_db.py \
     --data-path path/to/your/knowledge_base.json
   ```

## Running the Application

### Option 1: Full Stack (Recommended)

**Terminal 1** - Start FastAPI backend:
```bash
python -m uvicorn src.assistant.infrastructure.api:app --reload --port 8000
```

**Terminal 2** - Start Streamlit frontend:
```bash
streamlit run app.py
```

Access the UI at **http://localhost:8501**

### Option 2: API Only

Start the backend and interact via WebSocket or REST:

```bash
python -m uvicorn src.assistant.infrastructure.api:app --reload --port 8000
```

**WebSocket endpoint**: `ws://localhost:8000/ws/{thread_id}`

**REST endpoint**: `POST http://localhost:8000/api/chat`

Example REST request:
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password?",
    "thread_id": "user123"
  }'
```

## Testing & Evaluation

### Running Evaluations

The project includes a comprehensive evaluation framework using **Opik** with 122 test cases covering all departments.

```bash
python run_tools/evaluate_agent.py \
  --name evaluation_dataset \
  --data-path evaluation_data/evaluation_data.json \
  --nb-samples 20 \
  --workers 1
```

**Parameters**:
- `--name`: Dataset identifier in Opik
- `--data-path`: Path to JSON file with Q&A pairs
- `--nb-samples`: Number of samples to evaluate (max 122)
- `--workers`: Parallel workers (increase for faster evaluation)

### Evaluation Metrics

The system is evaluated on 5 key metrics using Opik's built-in evaluators:

| Metric | Score | Description |
|--------|-------|-------------|
| **Answer Relevance** | 94.8% | How well the response addresses the user's query |
| **Context Precision** | 96.0% | Accuracy of retrieved documents (RAG quality) |
| **Context Recall** | 89.0% | Completeness of retrieved information |
| **Hallucination** | 12.0% | Percentage of unsupported claims (lower is better) |
| **Moderation** | 0.0% | Content safety violations (0% = safe) |

**Key Insights**:
- **High relevance (94.8%)**: Agent consistently provides on-topic responses
- **Excellent precision (96%)**: RAG retrieval is highly accurate with minimal noise
- **Good recall (89%)**: Most relevant information is retrieved
- **Low hallucination (12%)**: Responses are well-grounded in retrieved context
- **Perfect moderation (0%)**: No safety concerns detected

### Sample Test Cases

The evaluation dataset includes:
- **HR queries**: Leave balance, expense claims, internal transfers
- **IT Support**: Password resets, account lockouts, access requests
- **Facilities**: Maintenance issues, meeting room bookings, kitchen policies
- **Billing**: Invoice downloads, unrecognized charges, payment methods
- **Shipping**: Delivery options, tracking, international shipping
- **General**: Greetings, capability questions, casual conversation

## API Documentation

### WebSocket API

**Endpoint**: `/ws/{thread_id}`

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Stream chunk:', data.content);
};

ws.send(JSON.stringify({
  message: "What are your shipping options?"
}));
```

**Streaming Response Format**:
```json
{
  "type": "stream",
  "content": "Partial response chunk...",
  "metadata": {
    "node": "generate_department_response"
  }
}
```

**Final Response Format**:
```json
{
  "type": "end",
  "content": "Complete final response",
  "metadata": {
    "query_category": "SHIPPING_AND_DELIVERY",
    "query_sentiment": "Neutral",
    "retrieved_content": "Context from vector DB..."
  }
}
```

### REST API

**Endpoint**: `POST /api/chat`

**Request Body**:
```json
{
  "message": "How do I view my past orders?",
  "thread_id": "user123"
}
```

**Response**:
```json
{
  "response": "You can view your past orders by logging into...",
  "metadata": {
    "query_category": "BILLING_AND_PAYMENT",
    "query_sentiment": "Neutral",
    "thread_id": "user123"
  }
}
```

## Memory & State Management

### Conversation Persistence

The chatbot uses **MongoDB checkpointing** to maintain conversation history across sessions:

1. **Thread-based isolation**: Each user gets a unique `thread_id` for their conversation
2. **Automatic checkpointing**: State is saved after each agent node execution
3. **Resume capability**: Users can disconnect and reconnect without losing context
4. **Message history**: Full conversation history available for context-aware responses

### State Schema

The agent state ([state.py](src/assistant/application/agents/state.py)) includes:

```python
class CustomerSupportAgentState(TypedDict):
    customer_query: Annotated[List[BaseMessage], add_messages]  # Message history
    query_category: str                                         # HR, IT, etc.
    query_sentiment: str                                        # Positive, Neutral, Negative
    retrieved_content: str                                      # RAG context
    final_response: str                                         # Agent's response
```

### MongoDB Collections

- **checkpoints**: Full state snapshots at each graph node
- **checkpoint_writes**: Incremental state updates for efficiency

### Thread Management

Example of retrieving conversation history:

```python
from src.assistant.application.generate_response import get_response

# Resume existing conversation
response = get_response(
    customer_query="What was my last question?",
    thread_id="user123"  # Same thread ID
)
```

## Future Enhancements

### Short-term
- [ ] **Multi-turn clarification**: Ask follow-up questions for ambiguous queries
- [ ] **Sentiment-based tone adaptation**: Adjust response empathy based on detected emotion
- [ ] **Confidence scoring**: Surface uncertainty with suggested human handoff
- [ ] **Multi-language support**: Translate queries/responses using GPT-4o
- [ ] **Admin dashboard**: Real-time monitoring of active conversations and metrics

### Medium-term
- [ ] **Fine-tuned categorization**: Train custom model on domain-specific queries
- [ ] **Hybrid retrieval**: Combine vector search with keyword BM25 for rare terms
- [ ] **Escalation logic**: Detect highly negative sentiment and route to human agents
- [ ] **Feedback loop**: Collect thumbs up/down to retrain models
- [ ] **A/B testing**: Compare prompt variations with Opik experiments

### Long-term
- [ ] **Voice interface**: Integrate Whisper (speech-to-text) and TTS
- [ ] **Multi-modal support**: Handle image uploads (e.g., screenshots of errors)
- [ ] **Proactive assistance**: Suggest help articles based on user behavior
- [ ] **Auto-knowledge ingestion**: Crawl company docs and auto-update vector DB
- [ ] **Custom LLM deployment**: Self-hosted model for data privacy

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **LangChain/LangGraph**: For the incredible agent orchestration framework
- **OpenAI**: For GPT-4o and embedding models
- **Qdrant**: For the high-performance vector database
- **Opik/Comet ML**: For evaluation and observability tools
- **MongoDB**: For reliable state persistence

## Contact

For questions or collaboration opportunities, reach out at:
- GitHub: [@yourusername](https://github.com/shima-maleki)
- Email: shimamaleki95@yahoo.com
- LinkedIn: [Your Name](https://www.linkedin.com/in/malekishima/)

---

**Built with LangGraph, OpenAI GPT-4o, Qdrant, and MongoDB Atlas**

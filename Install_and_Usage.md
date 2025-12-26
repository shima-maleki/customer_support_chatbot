# 🚀 Installation and Usage Guide
This guide will help you set up and run a ...

- **📑 Table of Contents**
- **📋 Prerequisites**
- **🎯 Getting Started**
- **📁 Project Structure**
- **⚡️ Running the Code for Each Module**

# 🛠️ Local Tools Setup

For all the modules, you'll need the following tools installed locally:

| Tool     | Version    | Purpose                                        | Installation Link |
|----------|------------|------------------------------------------------|-------------------|
| Python   | 3.11       | Programming language runtime                   | [Download](https://www.python.org/downloads/release/python-3110/) |
| uv       | ≥ 0.4.30   | Python package installer and virtual environment manager | [Download](https://github.com/astral-sh/uv) |
| GNU Make | ≥ 3.81     | Build automation tool                          | [Download](https://www.gnu.org/software/make/) |
| Git      | ≥ 2.44.0   | Version control                                | [Download](https://git-scm.com/downloads) |
| Docker   | ≥ 27.4.0   | Containerization platform                      | [Download](https://www.docker.com/products/docker-desktop/) |

> 📌 **Windows Users**: Also install [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install).

---

# ☁️ Cloud Services

The course requires access to the following cloud services. Authentication is done via environment variables set in your `.env` file:

| Service      | Purpose                         | Cost       | Environment Variable | Setup Guide                           | Starting with Module |
|--------------|----------------------------------|------------|-----------------------|----------------------------------------|----------------------|
| **Opik**     | LLMOps                           | Free tier  | `COMET_API_KEY`       | [Quick Start Guide](https://opik.ai)   | Module 5             |
| **OpenAI**   | LLM API used for evaluation      | Pay-per-use| `OPENAI_API_KEY`      | [Quick Start Guide](https://openai.com)| Module 5             |

> 💡 When working locally, the infrastructure is set up using Docker. You can use the default values from `config.py` for all infrastructure-related environment variables.

## Optional Deployment Services

If deploying the code externally, configure the following:

| Service    | Purpose              | Cost      | Required Credentials | Setup Guide                                                                 |
|------------|----------------------|-----------|-----------------------|------------------------------------------------------------------------------|
| **MongoDB**| Document database    | Free tier | `MONGODB_URI`         | 1. [Create MongoDB Atlas Account](https://www.mongodb.com/cloud/atlas)<br>2. Create a Cluster<br>3. Add a Database User<br>4. Configure Network Access |
| **QDrant**| Document database    | Free tier | `QDRANT_URI`         | 1. [Create MongoDB Atlas Account](https://cloud.qdrant.io/)<br>2. Create a Cluster<br>3. Add a Database User<br>4. Configure Network Access |

---

# 🚀 Getting Started

### 1. Clone the Repository

git clone https://github.com/Bhardwaj-Saurabh/customer_support_chatbot_Retail.git
cd customer_support_chatbot_Retail/


### 2. Installation
Inside the assistant directory, to install the dependencies and activate the virtual environment, run the following commands:

```
uv venv .venv
. ./.venv/bin/activate # or source ./.venv/bin/activate
uv pip install -e .
```
This command will:

Create a virtual environment with the Python version specified in .python-version using uv
Activate the virtual environment
Install all dependencies from pyproject.toml

### 3. Test that you have Python 3.11.9 installed in your new uv environment:
```
uv run python --version
```

- Output: Python 3.11.9

### 4. Environment Configuration
Before running any command, inside the philoagents-api directory, you have to set up your environment:

Create your environment file:
```
cp .env.example .env
```

Open .env and configure the required credentials following the inline comments and the recommendations from the Cloud Services section.

## 📁 Project Structure
The project follows a clean architecture structure commonly used in production Python projects:

```
├── evaluation_data
│   └── evaluation_data\evaluation_data.json
├── knowledge_base
│   ├── knowledge_base\billing_and_payment_data.json
│   ├── knowledge_base\delivery_and_shipping_data.json
│   ├── knowledge_base\facility_and_admin_data.json
│   ├── knowledge_base\hr_data.json
│   └── knowledge_base\it_support_data.json
├── notebooks
│   └── chatbot_experiment.ipynb
├── run_tools
│   ├── evaluate_agent.py
│   ├── ingest_data.py
│   └── main.py
├── src
│   └── \assistant
│       ├── application
│       ├── domain
│       ├── infrastructure
│       ├── config.py
│       └── utils.py
├── static
│   ├── Evaluation.png
    ├── domaingraph.png
├── .python-version
├── app.py
├── Dockerfile
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

# ⚡️ Running the Code for Each Module**

## To Ingest data:
```
python run_tools/ingest_data.py
```

## To Run cli application
```
python run_tools/main.py
```

## To Evaluate Agentic Flow
```
python run_tools/evaluate.py
```
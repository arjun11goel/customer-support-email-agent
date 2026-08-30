# SupportFlow AI: Customer Support Email Agent

> Agentic Customer Support Email System built with Python, FastAPI, LangGraph, LangChain, FAISS and Streamlit.

SupportFlow AI is a production-oriented AI engineering project that processes customer support emails through an agentic workflow.

The system is designed to classify customer intent, retrieve relevant knowledge, generate grounded responses, validate the response and route cases for human review.

---

## Current Status

**Initial scaffold**

The current version provides:

* FastAPI backend
* SQLite persistence
* Mock email creation
* Inbox API
* Email details API
* LangGraph workflow skeleton
* Knowledge-base structure
* FAISS retrieval structure
* Streamlit dashboard
* Test Agent page
* Inbox page
* Email Details page
* Knowledge Base page
* Repository layer
* Service layer
* Pydantic schemas
* Configuration management
* Logging
* Testing foundation
* Docker configuration

The actual LLM classification, RAG retrieval, response generation and validation will be implemented incrementally.

---

## Architecture

```text
Customer Email
      |
      v
 Email Provider
 Mock / Gmail / Outlook
      |
      v
    FastAPI
      |
      v
Application Services
      |
      v
   LangGraph
      |
      +----> Classification
      |
      +----> Knowledge Retrieval
      |
      +----> Response Generation
      |
      +----> Response Validation
      |
      +----> Escalation
      |
      v
Human Review
      |
      v
  Response
      |
      v
 Persistence
```

---

## Technology Stack

```text
Backend
    Python
    FastAPI
    Pydantic
    SQLAlchemy
    SQLite

AI
    LangGraph
    LangChain
    LangChain OpenAI-compatible interface
    Sentence Transformers
    FAISS

Frontend
    Streamlit

Testing
    Pytest
    FastAPI TestClient

Deployment
    Docker
    Free/local-first architecture
```

---

## Core Agent Workflow

```text
Incoming Email
      |
      v
Validate Email
      |
      v
Classify Intent
      |
      v
Retrieve Knowledge
      |
      v
Generate Response
      |
      v
Validate Response
      |
      v
Evaluate Escalation
      |
      v
Human Review
```

---

## Intent Categories

The system will classify emails into:

* Product Question
* Bug Report
* Billing Issue
* Feature Request
* Complex Issue
* Other

---

## Project Structure

```text
supportflow-ai/

├── app/
│   ├── api/
│   ├── ai/
│   ├── core/
│   ├── database/
│   ├── integrations/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
│
├── data/
│   ├── knowledge_base/
│   └── vector_store/
│
├── prompts/
├── scripts/
├── tests/
├── ui/
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Design Principles

### Separation of Concerns

The project separates:

* API
* Services
* AI workflow
* Retrieval
* Database
* Repositories
* Integrations
* UI

---

## Project Goal

The goal of SupportFlow AI is not to build a simple chatbot.

The goal is to demonstrate how an AI-powered support workflow can be engineered as a maintainable backend system with:

* Agent orchestration
* Retrieval augmented generation
* Structured outputs
* Validation
* Human-in-the-loop workflows
* API architecture
* Persistence
* Testing
* Provider abstraction
* Production-oriented design

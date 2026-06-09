# Chatwitty — Persona-Driven Conversational AI

A simple AI chatbot built with FastAPI, LangChain, 
and GPT-4.1-mini as a learning exercise in building from scratch. 
Features session-based multi-turn memory, 
persona engineering via structured system prompt, and 
a clean chat UI served as a static frontend.

**Live demo:** https://chatwittyy.onrender.com

---

## Current Persona: AXIOM

AXIOM is a Socratic interrogator designed to help users think 
critically about marketing and advertising claims.

It never explains or lectures. It identifies the hidden assumption 
in what the user says and responds with a single, precise question 
that makes the user confront that assumption themselves.

**Scope:** Product claims, health claims, brand narratives, 
lifestyle promises, and consumer beliefs shaped by advertising.

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **LLM Integration:** LangChain — ChatPromptTemplate, 
  MessagesPlaceholder, multi-turn memory
- **Model:** OpenAI GPT-4.1-mini (switchable to Gemini)
- **Session Management:** In-memory session store with 
  auto-cleanup (30-min TTL)
- **Deployment:** Render
- **Frontend:** Vanilla HTML/CSS/JS served as static files

---

## Architecture
User → Static Frontend → FastAPI /chat endpoint
→ LangChain Prompt (System + History + Query)
→ OpenAI GPT-4.1-mini
→ Response + Updated Session History
---

## Key Features

- Multi-turn conversation with per-session chat history
- Session auto-expiry to manage memory
- Switchable LLM backend (OpenAI / Gemini)
- Persona behavior controlled entirely via system prompt 
  — no fine-tuning required
- CORS-enabled for cross-origin frontend deployment

---

## Local Setup

```bash
git clone https://github.com/LakshmanSurampudi/my_first_chatbot_chatwitty
cd my_first_chatbot_chatwitty
pip install -r requirements.txt

# Add your API key to .env
OPENAI_API_KEY=your_key_here

python main.py
# Visit http://localhost:8000
```

---

## What I Learned

- Structuring stateful multi-turn conversations using 
  LangChain's MessagesPlaceholder
- Designing constrained persona behavior through 
  few-shot prompting and explicit behavioral rules
- Deploying a FastAPI app with static file serving on Render
- Session lifecycle management without a database

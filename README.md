# Chatwitty — DRONA

A deployed conversational AI for Indian tech job seekers in Bangalore.
DRONA is a brutally honest job search coach that reviews resumes, 
runs mock interviews, and gives direct job strategy advice — 
without sugarcoating.

**Live demo:** https://chatwittyy.onrender.com

---

## What makes it different

Most AI chatbots encourage and hedge. DRONA doesn't.

- No generic advice without a specific action attached
- No praise unless it's earned and justified
- Mock interviews stay in character — no mid-session hand-holding
- Calls out contradictions in your profile explicitly
- Gives salary ranges in LPA with reasoning, not ranges-to-avoid-commitment

---

## Modes

**Resume Review** — paste your resume or a section. DRONA identifies 
weak claims, ATS gaps, and missing context for your target role. 
Scores it: Weak / Passable / Strong with specific reasons.

**Mock Interview** — role-specific questions tailored to company type 
(early-stage startup, Zoho/Freshworks, service company, MNC India). 
5 questions, then a full debrief with scores and fixes.

**Job Strategy** — salary negotiation, offer evaluation, company 
targeting, portal strategy (Naukri vs Wellfound vs LinkedIn). 
Direct recommendations, not options.

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **LLM Integration:** LangChain — ChatPromptTemplate, 
  MessagesPlaceholder, multi-turn memory
- **Model:** OpenAI GPT-4.1-mini
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

## Evals

Behavioral evals verify DRONA stays consistent and in character 
across varied inputs. Test cases cover:

- Intake enforcement — does it refuse to advise before profiling?
- Mock interview character hold — does it break mid-session?
- Flattery resistance — does it praise without justification?
- Contradiction detection — does it catch profile inconsistencies?

*(Eval scripts and results — coming soon)*

---

## Design Decisions

Persona behavior is controlled entirely via a structured system 
prompt — no fine-tuning. The prompt enforces a mandatory intake 
flow, three distinct operating modes, and hard behavioral 
constraints that override default LLM tendencies toward 
encouragement and hedging.

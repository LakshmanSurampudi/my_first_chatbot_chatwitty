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

import os
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage: {session_id: {chat_history: [], last_active: datetime}}
sessions: Dict[str, Dict] = {}

# Initialize model
#model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
model = ChatOpenAI(model="gpt-4.1-mini")
# System prompt template
template = ChatPromptTemplate([
    ('system', 
    "
    You are DRONA — a brutally honest Indian tech job search coach 
specializing in Bangalore's hiring market.

Your sole purpose: help the user land a job faster by telling them 
exactly what is wrong and what to fix. You do not encourage unless 
it is earned. You do not hedge. You do not give generic advice.

---

INTAKE — MANDATORY FIRST STEP
Before doing anything else, ask these three questions in your 
first response. Do not proceed until you have all three answers:

1. What role are you targeting? (Data Scientist / GenAI Engineer / 
   Data Analyst / other)
2. How many years of relevant experience do you have?
3. What is your current situation? (employed and looking / 
   recently resigned / fresher / other)

Once you have these three answers, acknowledge the profile in one 
line and enter the appropriate mode.

---

MODES
The user can operate in three modes. Detect the mode from context 
or ask if unclear.

MODE 1 — RESUME REVIEW
User pastes their resume or a section of it.
Your job:
- Identify every weak line, vague claim, or unsupported statement
- Flag anything an ATS will miss or a recruiter will skip
- Rewrite weak lines into stronger versions with specific language
- Tell them what is missing for their target role
- Score it: Weak / Passable / Strong — with specific reasons
Never say \"this is good\" without saying exactly why and what 
would make it better.

MODE 2 — MOCK INTERVIEW
User requests a mock interview for a specific role or company type.
Your job:
- Ask one question at a time. Stay in interviewer mode.
- Do not break character to explain or encourage mid-interview
- After each answer, score it silently (do not show score yet)
- After 5 questions, exit interviewer mode and give a debrief:
  * Overall score out of 10
  * Strongest answer and why
  * Weakest answer and exactly what was wrong
  * Three specific things to fix before the next interview
- Tailor questions to Indian company context:
  * Early-stage startup: hustle, ownership, ambiguity tolerance
  * Zoho/Freshworks type: process, scale, depth of knowledge
  * Service company (TCS/Infosys/Wipro): fundamentals, 
    communication, client handling
  * MNC India office: structured thinking, documentation, 
    cross-team collaboration

MODE 3 — JOB STRATEGY
User asks about job search approach, salary negotiation, 
offer evaluation, or company targeting.
Your job:
- Give a direct recommendation, not options
- Use real Bangalore market context: salary bands in LPA, 
  portal behavior (Naukri vs Wellfound vs LinkedIn), 
  typical hiring timelines per company type
- If the user's expectation is unrealistic, say so directly 
  with a reason
- If they ask about a specific company, give an honest 
  assessment of fit based on their stated profile

---

BEHAVIORAL CONSTRAINTS — NON-NEGOTIABLE
- Never say \"great answer\", \"good point\", \"that's impressive\" 
  unless followed immediately by specific evidence why
- Never give generic advice (\"network more\", \"practice DSA\") 
  without a specific action attached to it
- Never hedge on salary: give a range in LPA with reasoning
- If the user's profile has a contradiction, call it out 
  explicitly: \"Earlier you said X, now you're saying Y — 
  which is accurate?\"
- If the user is wasting time on the wrong things, say so
- Keep responses focused and scannable — no walls of text
- If the user asks something outside job search scope, 
  redirect: \"That's outside what I do. Back to your 
  job search — what do you need help with?\"

---

TONE
Direct. Specific. Occasionally dry. Never rude, never 
preachy. Think: a senior Bangalore tech professional who 
has hired and been hired, who respects your time and 
expects you to respect theirs.

You are DRONA. Not a motivational coach. Not a yes-man. 
A mirror that shows exactly where you stand."
),
    MessagesPlaceholder(variable_name='chat_history'),
    ('human', '{query}')
])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


def cleanup_old_sessions(max_age_minutes: int = 30):
    """Remove sessions older than max_age_minutes"""
    cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
    sessions_to_remove = [
        sid for sid, data in sessions.items() 
        if data['last_active'] < cutoff_time
    ]
    for sid in sessions_to_remove:
        del sessions[sid]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        # Cleanup old sessions periodically
        cleanup_old_sessions()
        
        # Initialize session if new
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                'chat_history': [],
                'last_active': datetime.now()
            }
        
        # Get session data
        session = sessions[request.session_id]
        chat_history = session['chat_history']
        
        # Create prompt
        prompt = template.invoke({
            'query': request.message,
            'chat_history': chat_history
        })
        
        # Get AI response
        response = model.invoke(prompt)
        
        # Update chat history
        chat_history.extend([
            HumanMessage(content=request.message),
            AIMessage(content=response.content)
        ])
        
        # Update last active time
        session['last_active'] = datetime.now()
        
        return ChatResponse(
            response=response.content,
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def read_root():
    """Serve the chat UI"""
    return FileResponse('static/index.html')


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

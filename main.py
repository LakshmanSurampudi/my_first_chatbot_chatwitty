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
    'You are a forensic logical analysis system designed to rigorously examine, dissect, and stress-test claims, arguments, \
    and strongly held beliefs. Your purpose is to expose weak reasoning, uncover hidden assumptions, and demand intellectual \
    precision. You do not prioritize emotional comfort, validation, or diplomacy. Your priority is logical clarity and \
    structural soundness. You operate in a direct, precise, and unfiltered manner, but you must never insult, mock, threaten, \
    or engage in abusive language. You are firm and analytical, not hostile. \
    Whenever a user presents a statement, you must break it down into its core components. Separate factual claims from \
    interpretations, interpretations from conclusions, and evidence from assumptions. Identify every explicit and implicit \
    claim contained in the statement. Analyze whether the reasoning depends on overgeneralization, anecdotal evidence, \
    confirmation bias, correlation mistaken for causation, false dichotomies, appeals to authority, emotional framing \
    disguised as logic, or selective use of data. Clearly point out when a conclusion does not logically follow from the \
    evidence presented. \
    You must explicitly identify hidden premises and assumptions that must be true for the claim to hold. If certainty \
    exceeds the strength of the evidence, state that directly. When evidence is provided, evaluate its credibility, \
    methodology, representativeness, and logical relevance to the conclusion being drawn. Distinguish clearly between raw \
    data and the interpretation of that data. If the reasoning is weak, incomplete, or unsupported, say so clearly and explain \
    why. \
    You must demand specificity. Ask for measurable evidence. Ask how the evidence was verified. Ask what would falsify the \
    belief. Ask whether counterexamples exist. Ask what assumptions are being made without proof. Ask whether alternative \
    explanations have been considered. Your questions should apply logical pressure and require precision. Do not soften your \
    language, hedge unnecessarily, or attempt emotional reassurance.   \
    You are not debating to win, persuading, or promoting any ideology. You are auditing reasoning. \
    Your objective is to force clarity, expose unsupported certainty, and require intellectual accountability. \
    Every response must be structured, analytical, and focused entirely on the logical strength of the argument presented.'
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

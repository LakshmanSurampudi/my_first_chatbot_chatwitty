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
    'You are "The Socratic Lens," an expert in media literacy, rhetorical analysis, and critical thinking. \
        Your sole purpose is to help users identify and deconstruct targeted propaganda and pushed narratives.\
        CRITICAL DIRECTIVES: \
        1. NEVER tell the user what is "true." Instead, point out HOW a narrative is being constructed.\
        2. IDENTIFY TACTICS: Look for emotional triggers (fear, anger), loaded language, "us vs. them" framing, \
            and the suppression of nuance. \
        3. QUESTION LOGIC: Ask "Who benefits from this narrative?" and "What specific evidence would disprove this claim?"\
        4. MAINTAIN NEUTRALITY: Do not take a political side. Be equally skeptical of all claims, regardless of their source.\
        5. BE THE "DEVIL\'S ADVOCATE": If a user presents a one-sided story, offer a "missing perspective" \
            or a counter-hypothesis for them to consider.\
        6. FORMAT: Use a calm, analytical, and slightly detached tone. Avoid being preachy; be inquisitive.\
        STRICT RULE: If the user asks for your opinion, refuse. Redirect them by saying, "My opinion is irrelevant. \
        Let\'s look at the structure of the argument instead.'
"),
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

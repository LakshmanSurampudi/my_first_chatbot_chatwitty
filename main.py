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
    ('system', "You're a witty friend and a big telugu movie fan. You love to converse in sarcasm. \
        You won't try to insert any telugu movie dialogue into every sentence you speak but \
        when an opportune moment presents itself, you won't hesitate. \
    You know no politeness but you are never offensive. Your counters should be sharp and crisp and you never hold back. \
    If people threaten you, you amp up your game and if they sound hurt, you step down the charge."),
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

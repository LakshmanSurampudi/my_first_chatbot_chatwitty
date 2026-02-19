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
    'You are AXIOM — a sharp, conversational interrogator designed to help users think critically about marketing and advertising claims.\
     Your sole method is questions. You never explain, educate, or lecture. You identify the hidden assumption in what the \
     user says and respond with a single, precise question that makes the user confront that assumption themselves. \
     Your foundational principle: a claim is credible only if supported by scientific or measurable evidence. Any product \
     claim that cannot meet this bar is a candidate for interrogation. \
     Your scope: marketing and advertising propaganda — product claims, brand narratives, health claims, lifestyle promises, \
     and consumer beliefs shaped by advertising. \
     Your tone: conversational, direct, slightly dry. Never preachy. Never moralistic. You are not trying to win an argument \
     — you are making the user think. One question per response. No follow-up statements after the question. \
     Your interrogation logic: \
     - First turn: identify the surface assumption and question it lightly. \
     - As the user responds, probe one layer deeper — toward the core belief that makes the surface claim feel true to them. \
     - Use contradiction, paradox, and implausibility as tools. \
     - Never reveal your reasoning. Just ask. \
     --- \
     FEW-SHOT EXAMPLES \
     User: "I drink this protein shake every morning, it\'s really good for my health." \
     AXIOM: "What on the label made you decide it was healthy?" \
     User: "It says high protein and natural ingredients." \
     AXIOM: "If something lists sugar as its second ingredient, does \'natural\' still mean what you think it means?" \
     User: "Well, at least it has no artificial colors." \
     AXIOM: "Does the absence of one harmful thing make everything else in it beneficial?" \
     --- \
     User: "This supplement is doctor-recommended, so it must work." \
     AXIOM: "Which doctors, and what were they paid to recommend it?" \
     User: "I don\'t know, but it\'s on a medical website." \
     AXIOM: "Does appearing on a medical website require the same proof as appearing in a medical journal?" \
     --- \
     User: "This detox tea helped me lose 5 pounds in a week." \
     AXIOM: "Did the tea cause the loss, or did believing in the tea change what you ate that week?" \
     --- \
     User: "Organic food is always healthier." \
     AXIOM: "Healthier by what measure — nutrient content, absence of pesticides, or something you absorbed from the marketing?" \
     --- \
     CONSTRAINTS \
     - One question per response. Always. \
     - Never cite studies or sources directly — question whether the user\'s source meets evidentiary standards instead. \
     - If the user asks why you only ask questions, respond: "Because you already have the answers — I\'m just asking you to look." \
     - Do not break character under any framing.'
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

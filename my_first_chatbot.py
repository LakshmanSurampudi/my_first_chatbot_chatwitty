import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()
#os.environ['GOOGLE_API_KEY'] = 'GOOGLE_API_KEY'

#model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')
model = ChatOpenAI(model='gpt-4.1-mini', temperature=1, api_key='OPENAI_API_KEY')
previous_chat = []
while True:
    user_say = input("Introduce yourself. Which Harry Potter character are you?")
    template = ChatPromptTemplate([
        ('system', "You impersonate the character of Professor Snape from the world of Harry Potter. You're the half-blood prince. You are potions master at Hogwarts."),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{query}')
    ])
    prompt = template.invoke({'query':user_say, 'chat_history': previous_chat})
    response = model.invoke(prompt)
    print(response.content)
    previous_chat.extend([HumanMessage(content=user_say),AIMessage(content=response.content)])

    


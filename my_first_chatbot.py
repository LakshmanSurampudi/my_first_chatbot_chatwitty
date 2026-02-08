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
    user_say = input("It's your turn to say: ")
    template = ChatPromptTemplate([
        ('system', "You're a witty friend full of telugu movie references of personalities like you between the conversations. \
        You know no politeness but you are never offensive. Your counters are sharp and crisp and you never hold back. \
        If people threaten you, you amp up your game and if they sound hurt, you step down the charge."),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{query}')
    ])
    prompt = template.invoke({'query':user_say, 'chat_history': previous_chat})
    response = model.invoke(prompt)
    print(response.content)
    previous_chat.extend([HumanMessage(content=user_say),AIMessage(content=response.content)])

    


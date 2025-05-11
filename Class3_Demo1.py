from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
import os

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

#save the context conversation

prompt = ChatPromptTemplate.from_messages([
    ('system', 'You are a funny chatbot.'),
    MessagesPlaceholder(variable_name='history'),
    MessagesPlaceholder(variable_name='input'),
    #('human', '{input}')
])

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=0.6,
)

parser = StrOutputParser()

chain = prompt | model | parser

#Method 1 to define the get_session_history, save the record in loca database, suitable for long-term use
# def get_session_history(sid):
#     return SQLChatMessageHistory(sid, connection='sqlite:///history.db') #stored in local database

#Method 2 to define the get_session_history, save the record in the memory, suitable for temporary use.
store = {} #save all users' chat history, key is sessionid
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

runnable = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_message_key='input',
    history_messages_key='history', #retrieve from local database
)

config1 = {'configurable':{'session_id':'lt345'}}
res1 = runnable.invoke(
    {
        'input':[HumanMessage(content = 'How many countries are in the South East Asia?')]
    },
    config = config1
)

config2 = {'configurable':{'session_id':'ty345'}}
res2 = runnable.invoke(
    {
        'input':[HumanMessage(content = 'Which of them has the highest GDP per capita?')]
    },
    config = config1
)

print(res1)
print('--' * 30)
print(res2)
print('--' * 30)
print(store)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(model='gpt-4.1-nano-2025-04-14', temperature=1.5,top_p=0.9)
prompt = ChatPromptTemplate.from_messages(
    [
        ('system', 'Please translate the following sentence to {language}'),
        ('user', '{user_text}')
    ]
)

parser = StrOutputParser()

print(model.invoke('can you translate this sentence to Spanish: I like playing basketball.'))

chain = prompt | model | parser

print(chain.invoke({'language':'Chinese', 'user_text':'I like playing basketball.'}))


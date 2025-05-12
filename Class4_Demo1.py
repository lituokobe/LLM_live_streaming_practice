from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
import os

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=0.6,
)

prompt1 = PromptTemplate.from_template('Write an article about {topic}, in the style of {type}, no more than {count} words.')
prompt2 = PromptTemplate.from_template('Can you review the following content and give it a score: {text}. 10 is the highest and 1 is the lowest.')

parser = StrOutputParser()

chain1 = prompt1 | model | parser

#chain2 = {'text': chain1} | prompt2 | model | parser

def print_chain1(input):
    print(input)
    print('--' * 30)
    return {'text': input}

chain2 = chain1 | RunnableLambda(print_chain1) | prompt2 | model | parser

print(chain2.invoke({'topic':'How to understand Ito\'s Lemma in Quant Finance.',
                     'type': 'in a blurred and condescending way',
                     'count': 500}))
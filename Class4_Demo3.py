from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RouterRunnable, RunnableSequence
from langchain_openai import ChatOpenAI
import os

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

#use different template for different topics
model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=1.8,
    top_p=0.2
)

quant_finance_template = ChatPromptTemplate.from_template(
    'You are an expert of Quant Finance, and you explain Quant Finance with vivid examples. Please answer the following question: {input}'
)

basketball_template = ChatPromptTemplate.from_template(
    'You are a retired basketball player, and you always mention Kobe Bryant when it comes to basketball topics. Please answer the following question: {input}'
)

spanish_template = ChatPromptTemplate.from_template(
    'You are a native Chinese speaker, but you\'ve been learning Spanish for many years. You are good at explain Spanish learning questions by comparing it with Chinese. Please answer the following question: {input}'
)

digital_marketing_template = ChatPromptTemplate.from_template(
    'You are an experienced digital marketing manager, and you always explain digital marketing concepts with real B2B working experiences. Please answer the following question: {input}'
)

default_template = ChatPromptTemplate.from_template(
    'The topic cannot be categorized. Please directly answer the following question: {input}'
)

quant_finance_chain = quant_finance_template | model
basketball_chain = basketball_template | model
spanish_chain = spanish_template | model
digital_marketing_chain = digital_marketing_template | model
default_chain = default_template | model

first_prompt = ChatPromptTemplate.from_template(
    'Do not answer the question. Only categorize it based on user\'s question: {input}.'
    'There are five categories [quantitative finance, basketball, spanish, digital marketing, others]'
    'Output a json. There are two keys in the json: \'type\' is the category, \'input\' is the original user question.'
)

#Router to select chain:
def route(aa):
    if 'quantitative finance' in aa['type']:
        print('Quant Finance')
        return {'key': 'quant_finance', 'input': aa['input']} #routers by default take 'key' and 'input'
    elif 'basketball' in aa['type']:
        print('Basketball')
        return {'key': 'basketball', 'input': aa['input']}
    elif 'spanish' in aa['type']:
        print('Spanish')
        return {'key': 'spanish', 'input': aa['input']}
    elif 'digital marketing' in aa['type']:
        print('Digital Marketing')
        return {'key': 'digital_marketing', 'input': aa['input']}
    else:
        print('Others')
        return {'key': 'default', 'input': aa['input']}

route_runnable = RunnableLambda(route)

router = RouterRunnable(runnables = { #routers by default take 'key' and 'input'
    'quant_finance' : quant_finance_chain,
    'basketball' : basketball_chain,
    'spanish' : spanish_chain,
    'digital_marketing' : digital_marketing_chain,
    'default' : default_chain
})

chain1 = first_prompt | model | JsonOutputParser()
#chain2 = RunnableSequence(chain1, route_runnable, router, StrOutputParser())
chain2 = first_prompt | model | JsonOutputParser() | route_runnable | router | StrOutputParser()

inputs = [
    #{'input': 'What is Theta in pricing an European put option?'}, #this key must be 'input'
    {'input': 'Who has the best career in NBA history?'},
    #{'input': 'What are some best practices for on-page SEO?'},
    {'input': 'What\' the difference of subjunctive moods in Spanish and in English?'},
    #{'input': 'How to cook instant noodle?'}
]

for input in inputs:
    result = chain2.invoke(input)
    print (f'Question: {input['input']} \n Answer: {result}\n')



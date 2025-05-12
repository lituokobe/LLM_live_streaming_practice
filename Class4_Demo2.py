from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
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

gather_preference_prompt = ChatPromptTemplate.from_template(
    'The user has provided some preferences for picking a restaurant: {input_preference}\n'
    'Please summarize to a clear request.'
)

recommend_restaurant_prompt = ChatPromptTemplate.from_template(
    'Based on this request from user: {input_request}\n'
    'Please provide 3 most suitable restaurant and provide reasons: '
)

summarize_recommendations_prompt = ChatPromptTemplate.from_template(
    'These are the recommendations of restaurants: {input_recommendations}\n'
    'Please summarize them to 2-3 sentences for the user to make a quick judgement.'
)

chain = gather_preference_prompt | model | recommend_restaurant_prompt | model | summarize_recommendations_prompt | model | StrOutputParser()

print(chain.invoke({'input_preference': 'I don\'t know what to eat. But I am on a diet and I have a funny stomach now.'}))


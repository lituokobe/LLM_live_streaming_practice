import os

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.tools import TavilySearchResults
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

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

#Create a search tool
#search_tool = TavilySearch(max_results=3)
search_tool = TavilySearchResults(max_results=3)
"""
If your search bot requires detailed responses with extracted answers and images,
TavilySearchResults might be the better choice. 
If you need fast and efficient searches with basic filtering, TavilySearch is a solid option.
"""
# res = search_tool.invoke('What\'s the weather like tomorrow in Shijiazhuang?')
# print(res)

#Create an agent
tools = [search_tool]
agent = create_react_agent(model, tools)

resp = agent.invoke({'messages': [HumanMessage(content='Which city is the capital of Hebei province?')]})
print(resp['messages'][1].content)
resp = agent.invoke({'messages': 'What\'s the weather like tomorrow in Shijiazhuang?'})
print(resp['messages'][2])

# for chunk in agent.stream({'messages': [HumanMessage(content='What\'s the weather like tomorrow in Shijiazhuang?')]}):
#     print(chunk)
#     print('--' * 20)
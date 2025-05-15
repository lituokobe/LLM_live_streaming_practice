from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    #model='gpt-4.1-nano-2025-04-14',
    model='gpt-4o',
    temperature=0,
)

tavily_tool = TavilySearchResults(max_results=1)
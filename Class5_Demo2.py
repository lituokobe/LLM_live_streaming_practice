from langchain.agents import initialize_agent, AgentType
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.tools import tool, StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

import os

from pydantic_core.core_schema import arguments_schema

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=1.8,
    top_p=0.2
)


#Define a tool by using '@tool'
class SearchInput(BaseModel):
    query: str = Field(description="the keyword to search for")

@tool('my_search', args_schema = SearchInput, return_direct = True)
def my_search(query: str) -> str:
    """
    This is a tool function to search the data on the computer.
    """
    return 'I am a search tool'

#Define a tool to sort values by using 'StructuredTool'
class SortInput(BaseModel):
    num: str = Field(description="A comma-separated string of numbers to sort")

def sort_num(num: str):
    """
    Sort all the numbers
    """
    return sorted(eval(num))

sort_tool = StructuredTool.from_function(
    func = sort_num,
    name = 'sort_num',
    description = 'Sort all the numbers in the list from smallest to largest.',
    args_schema = SortInput,
    return_direct = True
)

tools = load_tools(['llm-math', 'arxiv'], model)
tools = [my_search, sort_tool] + tools

agent = initialize_agent(
    tools,
    model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True)


agent.invoke('calculate 2 multiples 3 and plus 7. The sort the following numbers, Action Input: 2,45,3,17,1')
#print(resp)
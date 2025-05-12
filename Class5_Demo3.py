import os

from langchain import hub
from langchain.agents import create_react_agent, create_structured_chat_agent, AgentExecutor
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from pydantic_core.core_schema import arguments_schema
from tenacity import retry_unless_exception_type

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=1.0,
)

#define a new tool
class ArgsInput(BaseModel):
    a: str = Field(description = 'first string')
    b: str = Field(description = 'second string')

def count_str(a:str, b:str) -> int:
    """
    Calculate the length of 2 strings and add them up.
    :param a:
    :param b:
    :return:
    """
    return len(a) + len(b)

len_add = StructuredTool.from_function(
    func=count_str,
    name='my_Calculator',
    description='Calculate total length of 2 strings.',
    args_schema=ArgsInput,
    return_direct=False
)

tools = [len_add]
prompt = hub.pull('hwchase17/structured-chat-agent')

agent = create_structured_chat_agent(model, tools, prompt)

#initialize an executor of the agent
agent_executor = AgentExecutor(agent = agent, tools = tools, verbose = False, handle_parsing_errors=True)
resp = agent_executor.invoke({'input':'what is total length of the string \'the missile is blocking\' and the string \'the tariff is dropping\'. What is LangSmith?'})
print(resp['output'])


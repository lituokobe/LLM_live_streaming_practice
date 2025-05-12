from langchain import hub
from langchain.agents import initialize_agent, AgentType, create_structured_chat_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.tools import tool, StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

llm = ChatOpenAI(
    temperature=1.0,
    model='gpt-4.1-nano-2025-04-14')


class ArgsInput(BaseModel):
    a: str = Field(description='第一个字符串')
    b: str = Field(description='第二个字符串')


def count_str(a: str, b: str) -> int:
    """分别计算两个字符串的长度，并且累加计算长度的和"""
    return len(a) + len(b)

# 2、结构化 得到一个工具
len_add = StructuredTool.from_function(
    func=count_str,  # 工具的函数
    name='my_Calculator',  # 一定是唯一的
    description='计算字符串长度的累加和',
    args_schema=ArgsInput,
    return_direct=False
)


tools = [len_add]
prompt = hub.pull('hwchase17/structured-chat-agent')
agent = create_structured_chat_agent(llm, tools, prompt)

# 初始化：agent的执行器
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

resp = agent_executor.invoke({'input': '`爱国者导弹拦截`的字符串长度加上`abc`字符串的长度是多少？ langsmith是什么？'})
print(resp)

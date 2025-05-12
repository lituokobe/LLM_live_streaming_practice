from langgraph.prebuilt import create_react_agent
from langchain.agents import initialize_agent, AgentType
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI

import os
os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=1.8,
    top_p=0.2
)

tools = load_tools(['llm-math', 'arxiv'], model)
#all the tools can be referred at https://python.langchain.com/docs/integrations/tools/

agent = initialize_agent( #create an general agent, this function tends to depreciate
    tools,
    model,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, #A zero shot agent that does a reasoning step before acting. This agent is designed to be used in conjunction
    handle_parsing_errors=True, #is parsing has errors, continue
    verbose = True
)

# resp = agent.invoke('What is 3 plus 2?')

resp = agent.invoke('Introduce the innovation point of essay 2007.1234?')

print(resp)
import os
from typing import Annotated

from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from Live_Streaming_practice.LangGraph_utils import draw_graph, loop_graph_invoke

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=1.0,
)

#Use LangGraph to build a chatbot
class MyState(TypedDict):
    #messages: the key stored in the state, the state is a dictionary
    messages: Annotated[list, add_messages]

#create a flowchart
graph = StateGraph(MyState)

#add a tool (internet search)
search_tool = TavilySearchResults(max_results=5)
tools = [search_tool]

#bind the tool with the model
agent = model.bind_tools(tools)

#prepare a node, input is a state, output is also a state, the state is a dictionary
def chatbot(state: MyState):
    return {'messages': [agent.invoke(state['messages'])]}

#Add the node to the graph
graph.add_node('agent', chatbot)

#add a tool node
tool_node = ToolNode(tools = tools)
graph.add_node('tools', tool_node)

#set up conditional edges to let agent deicide whether to use the tool
graph.add_conditional_edges('agent', tools_condition)

#set up other edges by creating an entry point
graph.add_edge('tools', 'agent')
graph.set_entry_point('agent')

graph = graph.compile()

#The graph is settled, make it a picture
#draw_graph(graph, 'graph2.png')


#execute the flow
while True:
    try:
        user_input = input('user: ')
        if user_input.lower() in['q', 'exit', 'quit']:
            print('The chat is over, bye-bye!')
            break
        else:
            loop_graph_invoke(graph, user_input)
    except Exception as e:
        print(e)
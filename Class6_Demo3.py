import os
from typing import Annotated

from langchain_community.tools import TavilySearchResults
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from Live_Streaming_practice.LangGraph_utils import draw_graph, loop_graph_invoke, loop_graph_invoke_tools

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

# save the conversation history to memory
memory_checkpointer = MemorySaver()

#you can also save the contxt conversation to SqliteSaver or PostgresSaver
#sqlite_checkpointer = SqliteSaver('sqlite:///test.db')

graph = graph.compile(
    checkpointer = memory_checkpointer, #define where the conversation history is saved
    interrupt_before=['tools'] #define an interruption point
)

#The graph is settled, make it a picture
#draw_graph(graph, 'graph3.png')

thread_id = input('please input a session id: ')
config = {'configurable': {'thread_id': thread_id}}

def get_answer(tool_message):
    #let human interference to provide an answer
    input_answer = input('User provides an answer:')
    answer = (
        input_answer
    )
    #create a message
    new_message = [
        ToolMessage(content=answer, tool_call_id = tool_message.tool_calls[0]['id']),
        AIMessage(content=answer),
    ]

    #put the human message to the workflow's state
    graph.update_state(
        config = config,
        values = {'messages': new_message},
    )

    for msg in graph.get_state(config).values['messages'][-2:]:
        msg.pretty_print()

#execute the flow
while True:
    try:
        user_input = input('user: ')
        if user_input.lower() in['q', 'exit', 'quit']:
            print('The chat is over, bye-bye!')
            break
        else:
            loop_graph_invoke(graph, user_input, config)
            #execute the folow
            now_state = graph.get_state(config)
            #check the status
            print('The current state is:', now_state)

            if 'tools' in now_state.next: #if the next node is tools
                #decide if human interference is needed
                tools_script_message = now_state.values['messages'][-1] #take the last value of the state
                print('Tools Script', tools_script_message.tool_calls)

                if input('User input whether to continue the tool? (y/n): ') == 'y':
                    # continue to next node: tools
                    loop_graph_invoke_tools(graph, None, config)
                else:
                    #if the user inputs n, they need to add a message by themselves
                    get_answer(tools_script_message)



            else:
                pass

    except Exception as e:
        print(e)
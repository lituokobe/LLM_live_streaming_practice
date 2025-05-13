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
from pydantic import BaseModel
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
#define the class of state
class MyState(TypedDict): #In the entire workflow, state is to store history
    #messages: the key to store history, add_messages is a function to update the list
    messages: Annotated[list, add_messages]
    #ask_person: the key to decide whether for human interference
    ask_person: bool

def create_response(response: str, ai_message: AIMessage):
    """
    Create a 'ToolMessage', it includes the human response content.
    :param response: the content of response
    :param ai_message: AI message object, get tool call ID from it
    :return: ToolMessage, it contains the response content and the message object of tool call id.
    """
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]['id'],
    )


class AskPersonMessage(BaseModel):
    """
    Redirect to human interference.
    If you cannot provide help, or the user request exceeds your capability, please use this function.
    To use it, please pass the user's request, so the human support will provide guidance.
    """
    request: str #the user's request that needs to pass to human interference

#create a flowchart
graph = StateGraph(MyState)

#add a tool (internet search)
search_tool = TavilySearchResults(max_results=1)
tools = [search_tool]

#bind the tool with the model
agent = model.bind_tools(tools+[AskPersonMessage])

#prepare a node, input is a state, output is also a state, the state is a dictionary
def chatbot(state: MyState):
    resp = agent.invoke(state['messages'])
    ask_person = False #by default, no need human service
    #if the response has tool calls, and first call's class is AskPersonMessage
    if resp.tool_calls and resp.tool_calls[0]['name'] == AskPersonMessage.__name__:
        ask_person = True #if this is True, we need human interference
    return {'messages': [resp], 'ask_person': ask_person}

#Add the node to the graph
graph.add_node('agent', chatbot)

#add a tool node
tool_node = ToolNode(tools = tools)
graph.add_node('tools', tool_node)

#add a node for human interference
def person_node(state: MyState):
    """
    process the logic to decide whether human interference is needed
    :param state:
    :return:
    """
    # create a message
    new_message = []
    #check if the last message is ToolMessage, if so, that means user input n
    if not isinstance(state['messages'][-1], ToolMessage):
        #if user input y, user will update state in break
        #if input n, we will pit a placeholder ToolMessage so LLM can continue process
        new_message.append(create_response('Human service is busy, please wait awhile.', state['messages'][-1]))

    return {
        'messages': new_message,
        'ask_person': False
    }

graph.add_node('person', person_node)

def select_next_node(state: MyState):
    """
    select next node based on current status
    :param state: dictionary of current node, include all the message and ask_person status
    :return: str of the next node name
    """
    if state['ask_person']: #if needed human interference, return person node
        return 'person'

    #or we can route to other nodes. Here, we use 'tools_condition' to decide the next.
    return tools_condition(state)

#set up conditional edges to let agent deicide whether to use the tool
graph.add_conditional_edges(
    'agent',
    select_next_node,
    {
        'person': 'person', #if returned person, select 'person' as next node
        'tools':'tools', #if returned tools, select 'tools' as next node
        END:END #if nothing, just end it
    }
)

#set up other edges by creating an entry point
graph.add_edge('tools', 'agent')
graph.add_edge('person', 'agent')
graph.set_entry_point('agent')

# save the conversation history to memory
memory_checkpointer = MemorySaver()

#you can also save the contxt conversation to SqliteSaver or PostgresSaver
#sqlite_checkpointer = SqliteSaver('sqlite:///test.db')

graph = graph.compile(
    checkpointer = memory_checkpointer, #define where the conversation history is saved
    interrupt_before=['person'] #define an interruption point
)

#The graph is settled, make it a picture
#draw_graph(graph, 'graph4.png')

thread_id = input('Please input a session id: ')
config = {'configurable': {'thread_id': thread_id}}

def get_answer(tool_message):
    #let human interference to provide an answer
    input_answer = input('Please input your reply to the user:')
    answer = (
        input_answer
    )
    #create a message
    person_message = create_response(answer, ai_message=tool_message)

    #put the newly created human message to the workflow's state
    graph.update_state(
        config = config,
        values = {'messages': [person_message]},
    )

    for msg in graph.get_state(config).values['messages'][-1:]:
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
            #print('The current state is:', now_state)

            if 'person' in now_state.next: #if the next node is 'tool'
                #human interference is needed
                tools_script_message = now_state.values['messages'][-1] #take the last value of the state
                print('Need human service', tools_script_message.tool_calls)

                if input('Can you provide human service?').lower() == 'y':
                    # continue to next node: tools
                    get_answer(tools_script_message) #let human create a message
                else:
                    #if the user inputs n, human service is busy
                    loop_graph_invoke_tools(graph, None, config)

    except Exception as e:
        print(e)
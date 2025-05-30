import os
from typing import Annotated
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import ToolMessage, AIMessage
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

#define the class of state
class MyState(TypedDict):
    messages: Annotated[list, add_messages]
    ask_person: bool

def create_response(response: str, ai_message: AIMessage):
    """
    Create a 'ToolMessage', it includes the human response content.
    :param response: the content of response
    :param ai_message: AI message object, get tool call ID from it
    :return: ToolMessage, it contains the response content and the message object of tool call id.
    """
    print(ai_message.tool_calls[0]['id'])
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
    request: str

#create a flowchart
graph = StateGraph(MyState)

#add tool
search_tool = TavilySearchResults(max_results=1)
tools = [search_tool]

#bind the tool to the model
agent = model.bind_tools(tools + [AskPersonMessage])

def chatbot(state: MyState):
    resp = agent.invoke(state['messages'])
    ask_person = False

    if resp.tool_calls and resp.tool_calls[0]['name'] == AskPersonMessage.__name__:
        ask_person = True
    return{'messages': [resp], 'ask_person':ask_person}

graph.add_node('agent', chatbot)

tool_node = ToolNode(tools = tools)
graph.add_node('tools', tool_node)

#add a node for human interference
def person_node(state: MyState):
    """
    Process the logic to decide whether human interference is needed
    :param state:
    :return:
    """
    new_message = []
    if not isinstance(state['messages'][-1], ToolMessage):
        new_message.append(create_response('Human service is busy, please wait..'), state['messages'][-1])

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
    if state['ask_person']:
        return 'person'

    return tools_condition(state)

graph.add_conditional_edges(
    'agent',
    select_next_node,
    {
        'person': 'person',
        'tools':'tools',
        END:END
    }
)

graph.add_edge('tools', 'agent')
graph.add_edge('person', 'agent')
graph.set_entry_point('agent')

memory_checkpointer = MemorySaver()

graph = graph.compile(
    checkpointer = memory_checkpointer,
    interrupt_before= ['person']
)

thread_id = input('Please input a session id: ')
config = {'configurable': {'thread_id': thread_id}}

def get_answer(tool_message):
    input_answer = input('Please input your reply to the user:')
    answer = (
        input_answer
    )
    person_message = create_response(answer, ai_message=tool_message)
    graph.update_state(
        config = config,
        values = {'messages': [person_message]}
    )

    for msg in graph.get_state(config).values['messages'][-1:]:
        msg.pretty_print()

while True:
    try:
        user_input = input('user: ')
        if user_input.lower() in ['exit', 'quit', 'q']:
            print('The chat is over, bye-bye!')
            break
        else:
            loop_graph_invoke(graph, user_input, config)

            now_state = graph.get_state(config)

            if 'person' in now_state.next:
                tools_script_message = now_state.values['messages'][-1]
                print('Need human service: ', tools_script_message.tool_calls)

                if input('Can you provide human service? (y/n): ').lower() == 'y':
                    get_answer(tools_script_message)

                else:
                    loop_graph_invoke_tools(graph, None, config)
    except Exception as e:
        print(e)
import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition


from Live_Streaming_practice.Ctrip_assistant.graph_chat.state import State
from Live_Streaming_practice.Ctrip_assistant.tools.flights_tools import fetch_user_flight_information
from Live_Streaming_practice.Ctrip_assistant.tools.init_db import update_dates
from Live_Streaming_practice.Ctrip_assistant.tools.tools_handler import create_tool_node_with_fallback, _print_event
from Live_Streaming_practice.Ctrip_assistant.graph_chat.assistant import create_assistant_node, part_1_tools
from Live_Streaming_practice.Ctrip_assistant.graph_chat.draw_png import draw_graph

#Define a flowchart's builder object
builder = StateGraph(State)

def get_user_info(state: State):
    """
    Obtain user's flight information and update the state dictionary.
    :param state: current state dictionary
    :return: state dictionary including user's new information
    """
    return {'user_info':fetch_user_flight_information.invoke({})}

#Run the node of 'fetch user info' first, meaning the assistant can see user's information before doing anything.
builder.add_node('fetch user info', get_user_info)

builder.add_edge(START, 'fetch user info')

#node can be customized function, runnable or customized class
builder.add_node('assistant', create_assistant_node())

builder.add_edge('fetch user info', 'assistant')

builder.add_node('tools', create_tool_node_with_fallback(part_1_tools))

builder.add_conditional_edges(
    'assistant',
    tools_condition, #build-in library in LangChain to let the model build the conditional edge. to use it you must have a node called 'tools'
)

builder.add_edge('tools', 'assistant')

memory = MemorySaver()

#set checkpointer to be memory, interrupt before going to tools.
graph = builder.compile(checkpointer=memory, interrupt_before=['tools'])

#draw_graph(graph, 'graph4.png')

session_id = str(uuid.uuid4())

update_dates() #Before testing everytime, make sure the time is good by updating the dates in the database
#only for this practice project. In real production environment, the database is updated in realtime.

config = {
    'configurable':{
        'passenger_id':'3442 587242',
        'thread_id': session_id,
    }
}

_printed = set() #make a set to avoid duplicated printing

#execute the workflow
while True:
    question = input('user: ')
    if question.lower() in ['quit', 'exit', 'q']:
        print('The chat is over, bye bye!')
        break
    else:
        events = graph.stream({'messages': ('user', question)}, config, stream_mode= 'values')
        #stream will output the result step by step, making it easier for interaction communication.
        #stream_mode is set 'values', meaning it will only output actual values, making the result cleaner
        #on the contrary, stream_mode can be set as 'objects', the output will be more complete but more complicated as well
        for event in events:
            _print_event(event, _printed)

        current_state = graph.get_state(config)
        if current_state.next:
            user_input = input('Do you approve this action? press \'y\' to continue, other wise please reiterate your request.')
            if user_input.strip().lower() == 'y':
                events = graph.stream(None, config, stream_mode= 'values')
                for event in events:
                    _print_event(event, _printed)
            else:
                result = graph.stream({
                    'messages': [
                        ToolMessage(
                            tool_call_id = event['messages'][-1].tool_calls[0]['id'],
                            content=f'User rejects to call the tool. The reason is {user_input}.'
                        )
                    ]
                },
                    config,
                )
                for event in events:
                    _print_event(event, _printed)



import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from Live_Streaming_practice.Ctrip_assistant.graph_chat.base_data_model import ToFlightBookingAssistant, \
    ToBookCarRental, ToHotelBookingAssistant, ToBookExcursion
from Live_Streaming_practice.Ctrip_assistant.graph_chat.build_child_graph import builder_hotel_graph, \
    builder_flight_graph, builder_car_graph, builder_excursion_graph
from Live_Streaming_practice.Ctrip_assistant.graph_chat.state import State
from Live_Streaming_practice.Ctrip_assistant.tools.flights_tools import fetch_user_flight_information
from Live_Streaming_practice.Ctrip_assistant.tools.init_db import update_dates
from Live_Streaming_practice.Ctrip_assistant.tools.tools_handler import create_tool_node_with_fallback, _print_event
from Live_Streaming_practice.Ctrip_assistant.graph_chat.assistant import CtripAssistant, assistant_runnable, primary_assistant_tools
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

#Run the node of 'fetch_user_info' first, meaning the assistant can see user's information before doing anything.
builder.add_node('fetch_user_info', get_user_info)
builder.add_edge(START, 'fetch_user_info')

#add child graphs for 4 special assistants
builder = builder_flight_graph(builder)
builder = builder_hotel_graph(builder)
builder = builder_car_graph(builder)
builder = builder_excursion_graph(builder)

#add primary assistant
builder.add_node('primary_assistant', CtripAssistant(assistant_runnable))
builder.add_node(
    'primary_assistant_tools', create_tool_node_with_fallback(primary_assistant_tools)
    #create_tool_node_with_fallback will select the tools from the list fairly, the fallback mechanism is to print out the error message.
)

def route_primary_assistant(state: dict):
    """
    Base on current state, decide route to special assistant node.
    :param state: dictionary of current state
    :return: node of next step
    """
    route = tools_condition(state)  # check next step
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls  # get the tool call of the last message
    if tool_calls:
        if tool_calls[0]["name"] == ToFlightBookingAssistant.__name__:
            return "enter_update_flight"  #to flight booking
        elif tool_calls[0]["name"] == ToBookCarRental.__name__:
            return "enter_book_car_rental"  # to car rental booking
        elif tool_calls[0]["name"] == ToHotelBookingAssistant.__name__:
            return "enter_book_hotel"  # to hotel booking
        elif tool_calls[0]["name"] == ToBookExcursion.__name__:
            return "enter_book_excursion"  # to excursion booking
        return "primary_assistant_tools"  # to primary assistant tool
    raise ValueError("Meaningless route")  # alert when noe appropriate tools found. Protective code as this barely happen.

builder.add_conditional_edges(
    'primary_assistant',
    route_primary_assistant,
    [
        'enter_update_flight',
        'enter_book_car_rental',
        'enter_book_hotel',
        'enter_book_excursion',
        'primary_assistant_tools',
        END,
    ]
)

builder.add_edge('primary_assistant_tools', 'primary_assistant')

#every assigned graph of special assistant can directly respond to the user. When the user reply, the message goes back to the current active graph.
def route_to_workflow(state: dict) -> str:
    """
    If we are assigned a task, directly route to relevant special assistant.
    :param state: current state dictionary
    :return: the node of next step
    """
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return 'primary_assistant' #if there is no state, go back to the primary assistant
    return dialog_state[-1]

builder.add_conditional_edges("fetch_user_info", route_to_workflow) #route based on user's info

memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=[
        'update_flight_sensitive_tools',
        'book_car_rental_sensitive_tools',
        'book_hotel_sensitive_tools',
        'book_excursion_sensitive_tools',
    ]
)

#draw_graph(graph, 'graph5.png')

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
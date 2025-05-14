from datetime import datetime

from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

from Live_Streaming_practice.Ctrip_assistant.graph_chat.state import State
from Live_Streaming_practice.Ctrip_assistant.tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, \
    cancel_car_rental
from Live_Streaming_practice.Ctrip_assistant.tools.flights_tools import fetch_user_flight_information, search_flights, \
    update_ticket_to_new_flight, cancel_ticket
from Live_Streaming_practice.Ctrip_assistant.tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel

from Live_Streaming_practice.Ctrip_assistant.tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, \
    cancel_excursion
from Live_Streaming_practice.Ctrip_assistant.tools.retriever_vector import lookup_policy


class CtripAssistant:
    #a customized class to act as a node in the flowchart
    def __init__(self, runnable: Runnable):
        """
        initialize the assistant's instance
        :param runnable: executable object, usually it's a Runnable
        """
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        """
        call the node, perform the assistant job
        :param state: current state
        :param config: configuration: passenger's info inside
        :return:
        """
        while True:
            #build a infinite loop, all the way till the result from self.runnable is effective
            #if it is not effective (e.g. no tools to call and the content is empty, or the content doesn't have expected format, keep the loop

            # The 3 lines below is to get the passenger's ID from the configuration and add it to state manually.
            # configuration = config.get('configurable', {})
            # user_id = configuration.get('passenger_id')
            # state={**state, 'user_info': user_id}

            result = self.runnable.invoke(state)
            #if after the runnbale is executed, there is no real output
            if not result.tool_calls and (#if no tools are called in the result, and the content is empty or the first element in the list has no 'text'
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get('text')
            ):
                messages = state['messages'] + [('user', 'Please provide a real input as response')]
                state = {**state, 'messages': messages}
            else: #if runnbale executed to have the needed result, break the loop
                break
        return {'messages': result}

tavily_tool = TavilySearchResults(max_results=1)

#all the tools
part_1_tools = [
    update_ticket_to_new_flight,
    cancel_ticket,
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
    book_hotel,
    update_hotel,
    cancel_hotel,
    book_excursion,
    update_excursion,
    cancel_excursion,
    tavily_tool,
    fetch_user_flight_information,
    search_flights,
    lookup_policy,
    search_car_rentals,
    search_hotels,
    search_trip_recommendations,
]

# list of tools which will be called in the interaction
sensitive_tools = [
    update_ticket_to_new_flight,
    cancel_ticket,
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
    book_hotel,
    update_hotel,
    cancel_hotel,
    book_excursion,
    update_excursion,
    cancel_excursion,
]

safe_tools = [
    tavily_tool,
    fetch_user_flight_information,
    search_flights,
    lookup_policy,
    search_car_rentals,
    search_hotels,
    search_trip_recommendations,
]

#this will be used to decide whether the user will need to confirm
sensitive_tools_name = {t.name for t in sensitive_tools}



def create_assistant_node() -> CtripAssistant:
    """
    create a node of assistant
    :return: return an object of CtripAssistant
    """
    model = ChatOpenAI(
        model='gpt-4.1-nano-2025-04-14',
        temperature=1.0,
    )
    #create a template for the primary assistant
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                'You are Ctrip\'s client assistant. Prioritize the provided tools to search flights, policies and other info to help users.'
                'When searching, please be persistent. If you fail at the first time, enlarge the searching scope.'
                'If the search result is empty, give up the enlarged searching scope. \n\ncurrent user:\n<User>\n{user_info}\n</User>'
                '\n current time:{time}.',
            ),
            ('placeholder', '{messages}'),
        ]
    ).partial(time=datetime.now())

    runnable =primary_assistant_prompt | model.bind_tools(safe_tools + sensitive_tools)
    return CtripAssistant(runnable)


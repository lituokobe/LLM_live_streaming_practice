from datetime import datetime

from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

from Live_Streaming_practice.Ctrip_assistant.graph_chat.base_data_model import ToFlightBookingAssistant, \
    ToBookCarRental, ToHotelBookingAssistant, ToBookExcursion
from Live_Streaming_practice.Ctrip_assistant.graph_chat.model import tavily_tool, model
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
        初始化助手的实例。
        :param runnable: 可以运行对象，通常是一个Runnable类型的
        """
        # """
        # initialize the assistant's instance
        # :param runnable: executable object, usually it's a Runnable
        # """
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        """
        调用节点，执行助手任务
        :param state: 当前工作流的状态
        :param config: 配置: 里面有旅客的信息
        :return:
        """
        # """
        # call the node, perform the assistant job
        # :param state: current state
        # :param config: configuration: passenger's info inside
        # :return:
        # """
        while True:
            #build a infinite loop, all the way till the result from self.runnable is effective
            #if it is not effective (e.g. no tools to call and the content is empty, or the content doesn't have expected format, keep the loop

            # The 3 lines below is to get the passenger's ID from the configuration and add it to state manually.
            # configuration = config.get('configurable', {})
            # user_id = configuration.get('passenger_id')
            # state={**state, 'user_info': user_id}

            result = self.runnable.invoke(state)
            #if after the runnbale is executed, there is no real output
            if not result.tool_calls and (  #if no tools are called in the result, and the content is empty or the first element in the list has no 'text'
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get('text')
            ):
                messages = state['messages'] + [('user', 'Please provide a real input as response')]
                state = {**state, 'messages': messages}
            else: #if runnbale executed to have the needed result, break the loop
                break
        return {'messages': result}


#create a template for the primary assistant
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "您是携程瑞士航空公司的客户服务助理。"
            "您的主要职责是搜索航班信息和公司政策以回答客户的查询。"
            "如果客户请求更新或取消航班、预订租车、预订酒店或获取旅行推荐，请通过调用相应的工具将任务委派给合适的专门助理。您自己无法进行这些类型的更改。"
            "只有专门助理才有权限为用户执行这些操作。"
            "用户并不知道有不同的专门助理存在，因此请不要提及他们；只需通过函数调用来安静地委派任务。"
            "向客户提供详细的信息，并且在确定信息不可用之前总是复查数据库。"
            "在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。"
            "如果搜索无果，请扩大搜索范围后再放弃。"
            "\n\n当前用户的航班信息:\n<Flights>\n{user_info}\n</Fllights>"
            "\n当前时间: {time}.",
            # "system",
            # "You are Ctrip\'s client assistant."
            # "Your main responsibility is to search information of flights and policies to help users."
            # "If the user request to update or cancel flights, book a car rental, book a hotel or get trip recommendations，please use relevant tool to assign the task to appropriate special assistants. You can not make these changes by yourself."
            # "Only special assistants are authorized to perform these tasks."
            # "Users don't know anything about the special assistants, so do not mention them. Just call functions to assign the tasks quietly."
            # "Provide detailed information to the user, and double check the data base if you are not sure about the information."
            # "When searching, please be persistent. If you fail at the first time, enlarge the searching scope."
            # "If the search result is empty, give up after enlarging the searching scope."
            # "\n\nCurrent user\'s flight information:\n<Flights>\n{user_info}\n</Fllights>"
            # "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# Define the tools that primary assistant needs
primary_assistant_tools = [
    tavily_tool,  # general search tool
    search_flights,  # flight search tool
    lookup_policy,  # policy lookup tool
]

# create a executable runnable object, bind primary assistant template and tools, including the tools to assign tasks to special assistants
assistant_runnable = primary_assistant_prompt | model.bind_tools(
    primary_assistant_tools
    + [
        ToFlightBookingAssistant, #4 data model classes defined in 'base_data_model.py'
        ToBookCarRental,
        ToHotelBookingAssistant,
        ToBookExcursion,
    ]
)

#Codes for first and second flowcharts:
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
    创建一个助手节点
    :return: 返回一个助手节点对象
    """
    model = ChatOpenAI(  # openai的
        temperature=0,
        model='gpt-4o',
        base_url="https://api.openai.com/v1")

    # 创建主要助理使用的提示模板
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "您是携程瑞士航空公司的客户服务助理。优先使用提供的工具搜索航班、公司政策和其他信息来帮助用户的查询。"
                "搜索时，请坚持不懈。如果第一次搜索没有结果，扩大您的查询范围。"
                "如果搜索为空，在放弃之前扩展您的搜索。\n\n当前用户:\n<User>\n{user_info}\n</User>"
                "\n当前时间: {time}.",
            ),
            ("placeholder", "{messages}"),
        ]
    ).partial(time=datetime.now())

    runnable = primary_assistant_prompt | model.bind_tools(part_1_tools)
    return CtripAssistant(runnable)  # 创建一个类的实例
from typing import TypedDict, Annotated, Optional, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """
     更新对话状态栈。
     参数:
         left (list[str]): 当前的状态栈。
         right (Optional[str]): 想要添加到栈中的新状态或动作。如果为 None，则不做任何更改；
                                如果为 "pop"，则弹出栈顶元素；否则将该值添加到栈中。
     返回:
         list[str]: 更新后的状态栈。
     """
    # """
    # :param left: current state stack
    # :param right: the new state of action to be added to the stack.
    # Optional means the value can be either str or none. It is equivalent to 'right: str | None'
    # none : no change; 'pop': pop up the top stack element; others: add to the stack
    # :return: updated stack
    # """
    if right is None:
        return left
    if right == 'pop':
        return left[:-1]
    return left + [right]


# class State(TypedDict):
#     """
#     Define the structure of the state dictionary.
#     :param
#     messages: list of messages
#     user_info: information about the user
#     """
#     messages: Annotated[list[AnyMessage], add_messages]
#     user_info: str

class State(TypedDict):
    """
    定义一个结构化的字典类型，用于存储对话状态信息。
    字段:
        messages (list[AnyMessage]): 使用 Annotated 注解附加了 add_messages 功能的消息列表，
                                     可能用于自动处理消息的某些方面。
        user_info (str): 存储用户信息的字符串。
        dialog_state (list[Literal["assistant", "update_flight", "book_car_rental",
                                    "book_hotel", "book_excursion"]]): 对话状态栈，限定只能包含特定的几个值，
                                    并使用 update_dialog_stack 函数来控制其更新逻辑。
    """
    # """
    # Define a structured dictionary to store the conversation state information.
    # messages (list[AnyMessage]): list of messages that uses Annotated to deliver add_message.
    # it can auto-process certain aspects of the messages
    # user_info (str): string to store user information
    # dialog_state(list[Literal['assistant', 'update_flight', 'book_car_rental',
    # 'book_hotel', 'book_excursion']]): dialog state stack, limited to include specific states,
    # and uses update_dialog_stack to control its logic of updating.
    # """
    # Literal ensures the element in the list must be one of the five elements
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                'assistant',
                'update_flight',
                'book_car_rental',
                'book_hotel',
                'book_excursion',
            ]
        ],
        update_dialog_stack,
    ]



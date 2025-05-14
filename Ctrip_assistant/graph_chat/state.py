from typing import TypedDict, Annotated, Optional, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """
    :param left: current state stack
    :param right: the new state of action to be added to the stack.
    Optional means the value can be either str or none. It is equivalent to 'right: str | None'
    none : no change; 'pop': pop up the top stack element; others: add to the stack
    :return: updated stack
    """
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
    Define a structured dictionary to store the conversation state information.
    messages (list[AnyMessage]): list of messages that uses Annotated to deliver add_message.
    it can auto-process certain aspects of the messages
    user_info (str): string to store user information
    dialog_state(list[Literal['assistant', 'update_flight', 'book_car_rental',
    'book_hotel', 'book_excursion']]): dialog state stack, limited to include specific states,
    and uses update_dialog_stack to control its logic of updating.
    """
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
                'book_excursion'
            ]
        ],
        update_dialog_stack,
    ]



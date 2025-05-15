from typing import Callable
from langchain_core.messages import ToolMessage

def create_entry_node(assistant_name: str, new_dialog_state) -> Callable:
    """
    This function create an entry node when switching state.
    It generates a new message and updates the state of the assistant.
    :param assistant_name: new assistant name or description
    :param new_dialog_state: the new state of the assistant
    :return: a function to process dialog state based on assistant_name and new_dialog_state
    """
    def entry_node(state: dict) -> dict:
        """
        根据当前对话状态生成新的对话消息并更新对话状态。

        :param state: 当前对话状态，包含所有消息。
        :return: 包含新消息和更新后的对话状态的字典。
        """
        # """
        # Generate new message and update the message state based on current message state.
        # :param state: current message state, including all the messages.
        # :return: dictionary with new messages and updated message state.
        # """
        #get the last message's tool ID
        tool_call_id = state['messages'][-1].tool_calls[0]['id']
        return {
            'messages': [
                ToolMessage(
                    content=f"现在助手是{assistant_name}。请回顾上述主助理与用户之间的对话。"
                            f"用户的意图尚未满足。使用提供的工具协助用户。记住，您是{assistant_name}，"
                            "并且预订、更新或其他操作未完成，直到成功调用了适当的工具。"
                            "如果用户改变主意或需要帮助进行其他任务，请调用CompleteOrEscalate函数让主要的主助理接管。"
                            "不要提及你是谁——仅作为助理的代理。",
                    # content=f'Currently the assistant is {assistant_name}, please review above conversation between primary assistant and the user'
                    #         f'User\'s request is not met yet. Use the provided tools to help user. Remember, you are {assistant_name}.'
                    #         f'Booking, update, or other operations are not yet done until the appropriate tool is called.'
                    #         f'If user changes mind or needs help for other tasks, please use function of CompleteOrEscalate to let primary assistant take over.'
                    #         f'Do not mention your identity, only act as the agent of assistant',
                    tool_call_id=tool_call_id,
                )
            ],
            'dialog_state': new_dialog_state,
        }

    return entry_node
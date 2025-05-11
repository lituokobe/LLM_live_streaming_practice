from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

llm_openai = ChatOpenAI(
    temperature=1.0,
    model='gpt-4.1-nano-2025-04-14')

# 上下文交互: 保存历史记录(存在哪里？)

parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ('system', '你是一个幽默的聊天机器人'),
    MessagesPlaceholder(variable_name='history'),
    ('human', '{input}')
])

# LCEL 表达式
chain = prompt | llm_openai | parser


# 把聊天记录保存本地数据库中
def get_session_history(sid):
    """
    根据会话的ID，读取和保存历史记录. 必须要BaseChatMessageHistory
    :param sid:
    :return:
    """
    return SQLChatMessageHistory(sid, 'sqlite:///history.db')


runnable = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='input',
    history_messages_key='history'
)

# 调用
res1 = runnable.invoke({'input': '中国一共有哪些直辖市？'}, config={'configurable': {'session_id': 'laoX002'}})

print(res1)
print('--' * 30)

res2 = runnable.invoke({'input': '这些城市中，哪个最大？'}, config={'configurable': {'session_id': 'laoX002'}})
print(res2)
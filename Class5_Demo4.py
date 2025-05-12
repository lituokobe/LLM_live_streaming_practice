import os
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from typing_extensions import TypedDict

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

model = ChatOpenAI(
    model='gpt-4.1-nano-2025-04-14',
    temperature=1.0,
)

#Use LangGraph to build a chatbot
class MyState(TypedDict):
    #messages: the key stored in the state, the state is a dictionary
    messages: Annotated[list, add_messages]

#create a flowchart
graph = StateGraph(MyState)

#prepare a node, input is a state, output is also a state, the state is a dictionary
def chatbot(state: MyState):
    return {'messages': [model.invoke(state['messages'])]}

#Add the node to the graph
graph.add_node('chatbot', chatbot)

#set up an edge
graph.add_edge(START, 'chatbot') #the flow starts from START to 'chatbot' which was added just now
graph.add_edge('chatbot', END)

#The graph is settled, make it a picture
print(type(graph))
graph = graph.compile()
print(type(graph))

# try:
#     #generate the image of graph
#     image = graph.get_graph().draw_mermaid_png()
#     with open('graph1.png', 'wb') as f:
#         f.write(image)
# except Exception as e:
#     print(e)

def loop_graph_invoke(user_input: str):
    """loop the flow, so the chatbot can keep the conversation."""
    for chunk in graph.stream({'messages': [('user', user_input)]}):
        for value in chunk.values():
            print('AI chatbot: ' , value['messages'][-1].content)

while True:
    try:
        user_input = input('user: ')
        if user_input.lower() in['q', 'exit', 'quit']:
            print('The chat is over, bye-bye!')
            break
        else:
            loop_graph_invoke(user_input)
    except Exception as e:
        print(e)
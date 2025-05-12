def draw_graph(graph, png_file):
    try:
        #generate the image of graph
        image = graph.get_graph().draw_mermaid_png()
        with open(png_file, 'wb') as f:
            f.write(image)
    except Exception as e:
        print(e)

def loop_graph_invoke(graph, user_input: str):
    """loop the flow, so the chatbot can keep the conversation."""
    # for chunk in graph.stream({'messages': [('user', user_input)]}):
    #     for value in chunk.values():
    #         print('AI chatbot: ' , value['messages'][-1].content)
    """ stream_mode = 'values' make the output simpler, only the actual values"""
    events = graph.stream({'messages': [('user', user_input)]}, stream_mode = 'values')
    for event in events:
        event['messages'][-1].pretty_print()

    # if user_input:
    #     events = graph.stream(
    #         {'messages': [('user', user_input)]}, stream_mode = 'values'
    #     )
    #     for event in events:
    #         if 'messages' in event:
    #             event['messages'][-1].pretty_print()
    # else: #output of the tool
    #     events = graph.stream(None,  stream_mode = 'values')
    #     for event in events:
    #         if 'messages' in event:
    #             event['messages'][-1].pretty_print()

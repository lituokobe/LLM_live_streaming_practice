import time
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI
import os

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

#1. create a runnable node
def test1 (x:int):
    return x+10

r1 = RunnableLambda(test1)

#2. batch
#res = r1.batch([3, 4, 6])

#3. streaming
# def test2(prompt:str):
#     for item in prompt.split(' '):
#         yield item
#         #yield allows iteration one step at a time. This is memory efficient, especially when working with large datasets.
#
# r1 = RunnableLambda(test2)
# res = r1.stream('I love quant finance.')
# for i in res:
#     print(i)

#4. chain
r1 = RunnableLambda(test1)
r2 = RunnableLambda(lambda x:x*2)
#
chain1 = r1 | r2
# print(chain.invoke(3))

#5. parallel
# chain = RunnableParallel(r1 = r1, r2 = r2)
# print(chain.invoke(2, config = {'max_concurrency': 10}))
#
# new_chain = chain1 | chain
# new_chain.get_graph().print_ascii() # 打印链的图像描述
# print(new_chain.invoke(2))

# 6. combine input and manage data in-between
r1 = RunnableLambda(lambda x: {'key1': x})
r2 = RunnableLambda(lambda x: x['key1']+10)
r3 = RunnableLambda(lambda x: x['new_key']['key2'])

#chain = r1 | RunnablePassthrough.assign(new_key = r2) #randomly create a data called 'new_key'
#chain = r1 | RunnablePassthrough()| RunnablePassthrough.assign(new_key = r2)
#chain = r1 | RunnableParallel(foo = RunnablePassthrough(), new_key=RunnablePassthrough.assign(new_key = r2))
# chain = r1 | RunnableParallel(foo = RunnablePassthrough(), new_key=RunnablePassthrough.assign(key2 = r2)) | RunnablePassthrough().pick(['new_key']) | r3
# print(chain.invoke(2))

# 7. fallback
# r1 = RunnableLambda(test1)
# r2 = RunnableLambda(lambda x:int(x) + 20)
# chain = r1.with_fallbacks([r2]) #if there is an error in r1, use r2
# print(chain.invoke('2'))

#8. run a note multiple times if there is an error
# counter = -1
#
# def test3 (x):
#     global counter
#     counter += 1
#     print(f'Executed {counter} times.')
#     return x/counter
#
# r1 = RunnableLambda(test3).with_retry(stop_after_attempt=4)
#
# print(r1.invoke(2))

#9. conditions
# r1 = RunnableLambda(test1)
# r2 = RunnableLambda(lambda x:[x]*2)
#
# chain = r1 | RunnableLambda(lambda x: r2 if x>12 else RunnableLambda(lambda x:x))
# print(chain.invoke(1))

#10. lifecycle
def test4(n:int):
    time.sleep(n)
    return n*2

r1 = RunnableLambda(test4)

def on_start(run_obj: Run):
    print('start time: ', run_obj.start_time)

def on_end(run_obj: Run):
    print('end time: ', run_obj.end_time)

chain = r1.with_listeners(on_start = on_start, on_end = on_end)  #this is to document the run time of a Runnable
print(chain.invoke(2))
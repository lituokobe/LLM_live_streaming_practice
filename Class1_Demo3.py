from openai import OpenAI
import ast
import numpy as np
import pandas as pd

client = OpenAI(
    base_url="https://api.openai.com/v1",
)

def cos_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def text_to_embedding(text, model):
    return client.embeddings.create(input=text, model=model).data[0].embedding

def search_text(df, text, top_n=3):
    input_vector = text_to_embedding(text, 'text-embedding-3-small')
    df['embedding_vector'] = df['embedding'].apply(ast.literal_eval)
    df['cos_similarity'] = df['embedding_vector'].apply(lambda x: cos_similarity(input_vector, x))

    res = (df.sort_values('cos_similarity', ascending=False)
           .head(top_n).text_content
           .str.replace('Summary: ', "")
           .str.replace('; Text: ', ';'))

    for i in res:
        print(i)
        print('*'*30)


df = pd.read_csv('../Class1/llm_demo01/openai_models/datas/output_embedding.csv')
search_text(df, 'fragrant pasta', top_n=3)
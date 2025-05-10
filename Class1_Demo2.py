import pandas as pd
from openai import OpenAI
import os

df = pd.read_csv('../Class1/llm_demo01/openai_models/datas/fine_food_reviews_1k.csv', index_col=0)

df = df[['Time', 'ProductId', 'UserId', 'Score', 'Summary', 'Text']]

#Process the data simply
df = df.dropna()
df['text_content'] = 'Summary: '+ df['Summary'].str.strip() + '; Text: '+ df['Text'].str.strip()

print(df.head())

client = OpenAI(
    base_url='https://api.openai.com/v1',
)

def text_embedding(text, model):
    return client.embeddings.create(input=text, model=model).data[0].embedding

df['embedding'] = df['text_content'].apply(lambda x: text_embedding(x, 'text-embedding-3-small'))

df.to_csv('../Class1/llm_demo01/openai_models/datas/output_embedding.csv')

print(df['embedding'][0])
from openai import OpenAI

client = OpenAI(
    base_url="https://api.openai.com/v1",  # URL of the target model, not necessarily to be OpenAI.
)

resp = client.embeddings.create(
    model = 'text-embedding-3-small',
    input = 'Italian language is a lot similar to Spanish than English.',
    dimensions = 512
)

print(resp)
print(resp.data[0].embedding)
print(len(resp.data[0].embedding) )

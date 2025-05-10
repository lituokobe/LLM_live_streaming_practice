from openai import OpenAI

client = OpenAI(
    base_url="https://api.openai.com/v1"
)

completion1 = client.chat.completions.create(
    model = 'gpt-4.1-nano-2025-04-14',
    temperature = 1.5,
    top_p = 0.9,
    messages = [
        {"role": "system", "content": "You are a happy assitant."},
        {"role": "user", "content": "Help me generate a Spanish learning plan in English. No more than 100 words."}
    ]
)

completion2 = client.chat.completions.create(
    model = 'gpt-4.1-nano-2025-04-14',
    temperature = 0.2,
    top_p = 0.1, #top_p is about word selections. It limits token selection to only the most probable words until their cumulative probability reaches the specified threshold
    messages = [
        {"role": "system", "content": "You are a happy assitant."},
        {"role": "user", "content": "Help me generate a Spanish learning plan in English. No more than 100 words."}
    ]
)

print(completion1)
print(completion1.choices[0].message)
print(completion1.choices[0].message.content)
print(completion2.choices[0].message.content)
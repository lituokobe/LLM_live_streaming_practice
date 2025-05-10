import requests
import json

url = 'https://api.openai.com/v1/chat/completions'

requests_data = json.dumps({
   "messages": [
      {
         "role": "system",
         "content": "You are an LLM chat bot."
      },
      {
         "role": "user",
         "content": "Let me know the country with the highest birth rate in 2023."
      }
   ],
   "stream": False,
   "model": "gpt-4.1-nano-2025-04-14",
   "temperature": 0.5,
   "presence_penalty": 0.2,
   "frequency_penalty": 0.2,
   "top_p": 1
})
headers = {
   'Authorization': 'Bearer api_key_here',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=requests_data)

print(response.text)
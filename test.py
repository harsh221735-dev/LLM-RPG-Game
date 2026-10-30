import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
response = requests.post(
  url="https://openrouter.ai/api/v1/embeddings",
  headers={
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
    #"HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    #"X-OpenRouter-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "liquid/lfm-2.5-embedding-350m:free",
    "input": "use black flash",
    # "input": ["text1", "text2", "text3"], # batch embeddings also supported!
    "encoding_format": "float"
  })
)
print(response.json()['data'][0]['embedding'])
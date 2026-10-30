# embeddings
from langchain_chroma import Chroma
import torch
from langchain_huggingface import HuggingFaceEmbeddings
import requests
from typing import List
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
import os
#from langchain_chroma import Chroma  # Preferred modern import

# loading main model
#from llama_cpp import Llama
# 1. Load the model into your 8GB RAM CPU
# we set n_ctx to 2048 to save RAM memory on your system
'''llm = Llama(
    model_path="C:\\Users\\ADMIN\\Desktop\\llm_poke_game\\qwen2.5-3b-instruct-q4_k_m.gguf",
    n_ctx=4096,  # Context window size
    n_threads=4  # Number of CPU cores to use (adjust based on your CPU)
)'''

#loading embedding model and database
current_device = 'cuda' if torch.cuda.is_available() else 'cpu'

embed_model = HuggingFaceEmbeddings(
    model_name = 'nomic-ai/nomic-embed-text-v1',
    model_kwargs = {'trust_remote_code': True, 'device':current_device}
    #encode_kwargs = {'prompt':'search_document'}
)



# Load environment variables from .env
#load_dotenv()

'''# 1. Define the Custom OpenRouter Embedding Class
class OpenRouterEmbeddings(Embeddings):
    def __init__(self, model_name: str = "liquid/lfm-2.5-embedding-350m:free"):
        self.model_name = model_name
        self.url = "https://openrouter.ai/api/v1/embeddings"
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not found.")

    def _get_embedding(self, text_input) -> List[List[float]]:
        """Helper method to make the HTTP POST request to OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "input": text_input,
            "encoding_format": "float"
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        response.raise_for_status() # Raises an error if the request failed (e.g. 429)
        
        response_json = response.json()
        
        # If input was a list, return list of vectors; if a string, return single nested vector list
        return [item["embedding"] for item in response_json["data"]]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents (supports batch processing)."""
        # OpenRouter accepts arrays of strings directly!
        return self._get_embedding(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single user search query string."""
        # Grab the first and only embedding from the returned list
        return self._get_embedding(text)[0]


# 2. Instantiate your custom model
embed_model = OpenRouterEmbeddings()'''

# 3. Pass it safely into your Chroma instance
persist_directory = "./my_chroma_db"

db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embed_model,
    collection_metadata={"hnsw:space": "cosine"}
)

print("Chroma DB initialized successfully using OpenRouter free embeddings!")

persist_directory = 'C:\\Users\\ADMIN\\Desktop\\llm_poke_game\\chroma_db'

db = Chroma(
    persist_directory=persist_directory,
    embedding_function= embed_model,
    collection_metadata={"hnsw:space":'cosine'}
)
def loaded_models():
    return db
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader    # Load the data
from langchain_text_splitters import CharacterTextSplitter                      # chunck the text
#from langchain_openai import OpenAIEmbeddings                                   # embeddings
from langchain_chroma import Chroma
#from langchain.embeddings import init_embeddings
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
import torch
import torch.nn.functional as F
current_device = "cuda" if torch.cuda.is_available() else "cpu"
embed_model = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1",
        model_kwargs={"trust_remote_code": True, "device": current_device},
        #encode_kwargs = {'prompt':'search_document'}
)


load_dotenv()

#loading the data 




#loading the data 
def load_documents(docs_path = r"C:\Users\ADMIN\Desktop\llm_poke_game\data"):
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The specified path '{docs_path}' does not exist.")

    loader = DirectoryLoader(
        path = docs_path,
        glob = "*.txt",
        loader_cls = TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(f"No text files found in the specified path '{docs_path}'.")   

    for i,doc in enumerate(documents):
        print(f"Document {i+1}: {doc.metadata['source']} - {len(doc.page_content)} characters")
        #print(f'Content : {doc.page_content[:100]}')
    return documents



# chuncking the text
def chunk_data(documents, chunk_size, chunk_overlap): #chunk overlap - num of prevous chunk's words in new one

    text_splitter = CharacterTextSplitter(separator='.',chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    chunks = text_splitter.split_documents(documents)

    for i,chunk in enumerate(chunks[:5]):
        print(f'chunk {i+1} : {chunk.metadata["source"]} - {len(chunk.page_content)} characters')
        #print(f'content : {chunk.page_content}')
    if len(chunks) >5:
        print(f'{len(chunks) - 5} more chunks remain')
    return chunks 
data = []

#using semantic chunking 

def semantic_1(chunks,window_size):
    i = 0
    n = window_size #window size
    j = 2*n 
    sim_list = {}
    #sliding window algorithm
    while j < len(chunks):
        window = chunks[i:j]
        #print(window)
        #averaging all sentence to 1 senetnce
        win1 = []
        for sent in range(len(window)//2):
            win1.append(window[sent].page_content)
        win1 = embed_model.embed_documents(win1)
        #print('win1',win1)
         #averaging all sentence to 1 senetnce
        win2 = []
        for sent in range(len(window)//2,len(window)):
            win2.append(window[sent].page_content)
        win2 = embed_model.embed_documents(win2)
        #print('length',len(win1),len(win2))
        #comapring

# 1. Compute your normalized cosine similarity matrix
        win1_tensor = torch.tensor(win1, dtype=torch.float32)
        win2_tensor = torch.tensor(win2, dtype=torch.float32)
        
        matrix1_norm = F.normalize(win1_tensor, p=2, dim=1) # (318, 768) p = eulicdean dist(2)
        matrix2_norm = F.normalize(win2_tensor, p=2, dim=1) # (459, 768)
        sim_matrix = torch.mm(matrix1_norm, matrix2_norm.t()) # (318, 459)
        
        # 2. Your Exact Logic: Get the max score for each token, then average
        # .max(dim=1) looks across the 459 tokens of Sentence 2 for each row
        # Direction 1 (Sentence 1 to 2)
        sim_1_to_2 = sim_matrix.max(dim=1).values.mean()

# Direction 2 (Sentence 2 to 1)
        sim_2_to_1 = sim_matrix.max(dim=0).values.mean()

# Combine them using F1-Score logic for a robust, symmetric scalar
        f1_similarity = 2 * (sim_1_to_2 * sim_2_to_1) / (sim_1_to_2 + sim_2_to_1)

        #print('precision:',sim_1_to_2)
        #print('recall:',sim_2_to_1)
        #print(f"Global Max Average Score: {f1_similarity:.4f}")

        # simillaryt is matrix right now so avergaing the matrix to scalar value
        sim_list[(j+i)//2] = f1_similarity.item()
        i = i + 1
        j = j + 1
    #print('sim_list',sim_list)
    #print(len(sim_list))
    # finding percentile threshold
    sorted_list = sorted(sim_list.values())
    percentile = 65
    index = (percentile/100) * len(sim_list)
    threshold = sorted_list[int(index)]
    print('threshold',threshold)

    # getting index on where to split based on threhold
    split_index = set()
    for (key,val) in sim_list.items():
        if val < threshold:
            split_index.add(key)
    print('split_index',split_index)
    #print(len(split_index))
    # actually dividing the data by index list(set)
    i = 0
    splitted_chunks = []
    for j in split_index:
        temp = []
        for k in range(i,j):
            temp.append(chunks[k].page_content)
        #print(temp)
        splitted_chunks.append('.'.join(temp))
        i = j
    print(splitted_chunks[:3])
    return sim_list,splitted_chunks


#create embeddings and store in vector database

#current_device = "cuda" if torch.cuda.is_available() else "cpu"

def create_embeddings(chunks, persist_directory):
    
    # create chromadb vector db
    vector_db = Chroma.from_texts(
        texts=chunks,  # Expects raw strings
        embedding=embed_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": 'cosine'}
    )

    print(f'Vector database created and persisted at {persist_directory}')
    return vector_db

    #for file in os.listdir('data'):
        #if file.endswith('.txt'):
            #print('file found')
db_path = 'C:\\Users\\ADMIN\\Desktop\\llm_poke_game\\chroma_db' # Using a dedicated subfolder is safer      
documents = load_documents()
    #print(documents)
chunks = chunk_data(documents,1,0)
sim_list,splitted_chunks = semantic_1(chunks,1)
create_embeddings(splitted_chunks, persist_directory=db_path)

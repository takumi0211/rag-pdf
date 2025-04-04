# --- START OF FILE get_embedding_function.py ---

from langchain_community.embeddings.ollama import OllamaEmbeddings

def get_embedding_function():
    # Ensure your Ollama embedding model name is correct
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    return embedding

# --- END OF FILE get_embedding_function.py ---
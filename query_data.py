# --- START OF FILE query_data.py ---

import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function
import os # Import os to check path

# Standardize Chroma path
CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Check if DB exists before querying in CLI mode
    if not os.path.exists(CHROMA_PATH):
         print(f"Error: Chroma database not found at path: {CHROMA_PATH}")
         print("Please populate the database first, e.g., using 'python populate_database.py'.")
         return

    response, sources = query_rag(query_text)
    print("Response:", response)
    print("Sources:", sources)

def query_rag(query_text: str):
    # Prepare the DB
    embedding_function = get_embedding_function()

    # Ensure DB exists before attempting to load
    if not os.path.exists(CHROMA_PATH):
         # This case should ideally be handled by the caller (like app.py)
         # but adding a check here provides another layer of safety.
         print(f"Warning: Chroma database path '{CHROMA_PATH}' does not exist in query_rag.")
         return "データベースが存在しません。", [] # Return error message and empty sources

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the database
    try:
        results = db.similarity_search_with_score(query_text, k=5)
    except Exception as e:
         # Handle potential errors during search (e.g., DB corruption, empty DB issues)
         print(f"Error during similarity search: {e}")
         # Depending on the error, you might want different responses.
         # If the DB is empty after creation, search might behave unexpectedly.
         # Check if results were obtained
         if 'results' not in locals() or not results:
              print("No results found, database might be empty or query yielded nothing.")
              return "データベース内で関連情報が見つかりませんでした。", []


    if not results:
         print("No relevant documents found in the database for the query.")
         return "関連情報が見つかりませんでした。", []

    # Format context and prompt
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print("--- PROMPT ---") # Optional: Debugging
    # print(prompt)
    # print("--- END PROMPT ---")

    # Generate response using the LLM
    try:
        model = Ollama(model="gemma3:4b") # Ensure your Ollama model name is correct
        response_text = model.invoke(prompt)
    except Exception as e:
         print(f"Error invoking Ollama model: {e}")
         return "言語モデルの呼び出し中にエラーが発生しました。", []

    # Extract sources
    sources = [doc.metadata.get("id", doc.metadata.get("source", "Unknown source")) for doc, _score in results]

    return response_text, sources


if __name__ == "__main__":
    main()
# --- END OF FILE query_data.py ---
# --- START OF FILE populate_database.py ---

import argparse
import os
import shutil
# Use PyPDFLoader for single files
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma

# Standardize Chroma path
CHROMA_PATH = "chroma"
DATA_PATH = "data"


# --- Core Logic Functions (Reusable) ---

def load_documents_from_directory(directory_path):
    """Loads all PDFs from a directory."""
    document_loader = PyPDFDirectoryLoader(directory_path)
    return document_loader.load()

def load_single_pdf(file_path):
    """Loads a single PDF document."""
    document_loader = PyPDFLoader(file_path)
    return document_loader.load()

def split_documents(documents: list[Document]):
    """Splits documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def calculate_chunk_ids(chunks):
    """Calculates unique IDs for document chunks."""
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # Handle potential missing page numbers gracefully
        if page is None:
             current_page_id = f"{source}:_page_unknown_" # Assign a default page marker

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id
    return chunks

def add_to_chroma(chunks: list[Document]):
    """Adds document chunks to the Chroma database."""
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    chunks_with_ids = calculate_chunk_ids(chunks)

    # Check existing IDs before adding
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if new_chunks:
        print(f"👉 Adding {len(new_chunks)} new documents")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
        print("✅ New documents added successfully.")
    else:
        print("✅ No new documents to add.")

def clear_database():
    """Clears the Chroma database."""
    if os.path.exists(CHROMA_PATH):
        print(f"🗑️ Removing Chroma database at {CHROMA_PATH}")
        shutil.rmtree(CHROMA_PATH)
        print("✅ Database cleared.")
    else:
        print("ℹ️ Chroma database path not found, nothing to clear.")


# --- New Function to Process a Single PDF ---
def process_pdf(file_path: str):
    """Loads, splits, and adds a single PDF to the Chroma database."""
    print(f"⏳ Processing PDF: {file_path}")
    try:
        documents = load_single_pdf(file_path)
        if not documents:
            print(f"⚠️ No documents loaded from {file_path}. Skipping.")
            return False

        chunks = split_documents(documents)
        if not chunks:
            print(f"⚠️ No chunks created from {file_path}. Skipping.")
            return False

        add_to_chroma(chunks)
        print(f"✅ Successfully processed and added {file_path} to the database.")
        return True
    except Exception as e:
        print(f"❌ Error processing PDF {file_path}: {e}")
        return False


# --- Main function for command-line execution (batch processing) ---
def main():
    parser = argparse.ArgumentParser(description="Populate or reset the Chroma vector store.")
    parser.add_argument(
        "--reset", action="store_true", help="Reset the database before processing."
    )
    parser.add_argument(
        "--path", type=str, default=DATA_PATH, help="Path to the directory containing PDFs."
    )
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database...")
        clear_database()

    # Check if the data path exists before trying to load
    if not os.path.exists(args.path):
         print(f"⚠️ Data path '{args.path}' not found. No directory processing will occur.")
         # If resetting, DB is cleared. If not resetting, maybe DB already exists.
         # If --path was specified but invalid, warn the user.
         if args.path != DATA_PATH: # User specified a custom path that doesn't exist
              print(f"❌ Error: Specified data path '{args.path}' does not exist.")
         return # Exit if no data path

    # Load documents from directory and add them
    print(f"📚 Loading documents from directory: {args.path}")
    documents = load_documents_from_directory(args.path)
    if documents:
        chunks = split_documents(documents)
        add_to_chroma(chunks)
    else:
        print(f"ℹ️ No documents found in {args.path}.")

if __name__ == "__main__":
    main()
# --- END OF FILE populate_database.py ---
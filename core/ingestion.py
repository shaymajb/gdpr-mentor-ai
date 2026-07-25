import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from langchain_community.document_loaders import PyMuPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def run_ingestion():
    data_path = "./data"
    db_path = "./db"

    if not os.path.exists(data_path):
        print("Error : create a 'data' folder and put your PDFs inside.")
        return

    pdf_files = [f for f in os.listdir(data_path) if f.endswith(".pdf")]
    if not pdf_files:
        print("Error : no PDF found in data/ folder.")
        return

    print(f"--- 1. Loading documents ({len(pdf_files)} PDFs found) ---")
    
    # Load each PDF individually to skip any problematic ones
    documents = []
    for pdf_file in pdf_files:
        try:
            loader = PyMuPDFLoader(os.path.join(data_path, pdf_file))
            docs = loader.load()
            documents.extend(docs)
            print(f"    OK : {pdf_file} ({len(docs)} pages)")
        except Exception as e:
            print(f"    SKIPPED : {pdf_file} — {e}")

    print(f"    Total : {len(documents)} pages loaded.")

    print("--- 2. Chunking ---")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)
    print(f"    {len(chunks)} chunks created.")

    print("--- 3. Generating embeddings ---")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    print("--- 4. Saving to ChromaDB ---")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_path
    )

    print(f"Done. {len(chunks)} chunks indexed in {db_path}/")

if __name__ == "__main__":
    run_ingestion()
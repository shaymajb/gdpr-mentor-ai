import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # ← change ici
from langchain_chroma import Chroma

def demarrer_archivage():
    if not os.path.exists("./data"):
        print("Erreur : Créez un dossier 'data' et mettez vos PDF dedans.")
        return

    print("--- 1. Chargement des documents ENA ---")
    loader = DirectoryLoader('./data', glob="./*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"    {len(documents)} pages chargées.")

    print("--- 2. Découpage des textes (Chunking) ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100
    )
    textes_decoupes = text_splitter.split_documents(documents)
    print(f"    {len(textes_decoupes)} chunks créés.")

    print("--- 3. Transformation en vecteurs (Embeddings) ---")
    embeddings = HuggingFaceEmbeddings(      # ← change ici
        model_name="all-MiniLM-L6-v2"
    )

    print("--- 4. Sauvegarde dans ChromaDB ---")
    Chroma.from_documents(
        documents=textes_decoupes,
        embedding=embeddings,
        persist_directory="./db"
    )
    print("Succès ! Base de connaissance ENA prête dans /db.")

if __name__ == "__main__":
    demarrer_archivage()
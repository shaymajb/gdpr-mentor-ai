import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")

vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

count = vectorstore._collection.count()
print(f"Nombre de chunks dans ChromaDB : {count}")

if count > 0:
    results = vectorstore.similarity_search("marches publics", k=3)
    print(f"Test recherche : {len(results)} resultats trouves")
    for r in results:
        print(f"  → {r.page_content[:120]}...")
else:
    print("Base VIDE")
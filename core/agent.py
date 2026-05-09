import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage

# ─────────────────────────────────────────
# Initialisation LLM + Embeddings + VectorDB
# ─────────────────────────────────────────
llm = OllamaLLM(model="mistral")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "db"
)
vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# ─────────────────────────────────────────
# AGENT PRINCIPAL — décision automatique
# ─────────────────────────────────────────
def interroger_agent(question: str, historique: list = []) -> str:
    """
    Agent ENA-Mentor :
    - Detecte le mode (RAG, simulation, evaluation)
    - Appelle le bon traitement automatiquement
    - Retourne une reponse structuree
    """
    q = question.lower()

    # MODE SIMULATION
    if any(mot in q for mot in [
        "simul", "scenario", "crise", "gouverneur",
        "jeu de role", "roleplay", "exercice", "genere"
    ]):
        return _simuler(question)

    # MODE EVALUATION
    elif any(mot in q for mot in [
        "evalue", "note", "feedback", "ma reponse",
        "qu'est-ce que tu penses", "correct", "donne moi un feedback"
    ]):
        return _evaluer(question)

    # MODE RAG (defaut)
    else:
        return _chercher(question, historique)


# ─────────────────────────────────────────
# TOOL 1 — Recherche dans ChromaDB
# ─────────────────────────────────────────
def _chercher(question: str, historique: list = []) -> str:
    docs = vectorstore.similarity_search(question, k=3)

    if not docs:
        return (
            "Je n'ai pas trouve de documents pertinents "
            "dans la base ENA pour cette question. "
            "Essayez de reformuler ou ajoutez des documents "
            "dans le dossier data/."
        )

    # Construction du contexte depuis les PDFs
    contexte = ""
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Document ENA")
        source = os.path.basename(source)
        contexte += f"\n[Document {i+1} — {source}]\n{doc.page_content}\n"

    # Construction de l'historique
    historique_txt = ""
    for msg in historique[-4:]:
        if isinstance(msg, HumanMessage):
            historique_txt += f"Eleve: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            historique_txt += f"Mentor: {msg.content}\n"

    prompt = f"""Tu es ENA-Mentor, l'assistant intelligent de l'Ecole Nationale
d'Administration tunisienne. Tu aides les eleves et fonctionnaires tunisiens.

HISTORIQUE :
{historique_txt if historique_txt else "Debut de conversation"}

DOCUMENTS DE REFERENCE TROUVES DANS LA BASE ENA :
{contexte}

QUESTION : {question}

INSTRUCTIONS :
- Reponds UNIQUEMENT en te basant sur les documents fournis
- Si la reponse n'est pas dans les documents, dis-le clairement
- Structure ta reponse avec des points clairs
- Cite le document source entre parentheses
- Reponds en francais, de facon pedagogique et precise"""

    return llm.invoke(prompt)


# ─────────────────────────────────────────
# TOOL 2 — Generateur de scenario de crise
# ─────────────────────────────────────────
def _simuler(theme: str) -> str:
    prompt = f"""Tu es un formateur expert a l'Ecole Nationale d'Administration tunisienne.

Genere un scenario de simulation de crise sur : {theme}

Structure obligatoire :
🗺️ CONTEXTE : lieu precis en Tunisie, date, heure
🎭 VOTRE ROLE : poste occupe (Gouverneur, Directeur, etc.)
📊 DONNEES DISPONIBLES : ressources et informations
⚡ LA CRISE : ce qui vient de se passer
❓ VOTRE DECISION : la question principale a resoudre

Sois precis et realiste pour un fonctionnaire tunisien."""

    return llm.invoke(prompt)


# ─────────────────────────────────────────
# TOOL 3 — Evaluateur de reponse
# ─────────────────────────────────────────
def _evaluer(reponse: str) -> str:
    prompt = f"""Tu es un evaluateur expert a l'Ecole Nationale d'Administration tunisienne.

Evalue cette reponse d'un apprenant :
"{reponse}"

Structure ton evaluation :
✅ POINTS FORTS : ce qui est bien decide
⚠️  POINTS A AMELIORER : ce qui manque ou est incorrect
📚 CADRE LEGAL TUNISIEN : procedures administratives applicables
🏆 NOTE : X/10 avec justification courte

Sois constructif et pedagogique."""

    return llm.invoke(prompt)
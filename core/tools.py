from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.tools import tool

# Initialisation LLM et VectorDB
llm = OllamaLLM(model="mistral")
embeddings = OllamaEmbeddings(model="mistral")
vectorstore = Chroma(
    persist_directory="./db",
    embedding_function=embeddings
)

# ─────────────────────────────────────────
# TOOL 1 — Recherche dans la base ENA
# ─────────────────────────────────────────
@tool
def search_documents(query: str) -> str:
    """
    Cherche dans la base de connaissance ENA les passages
    les plus pertinents pour répondre à une question documentaire.
    Utilise cet outil pour toute question sur les lois,
    mémoires, procédures ou textes administratifs tunisiens.
    """
    docs = vectorstore.similarity_search(query, k=3)

    if not docs:
        return "Aucun document pertinent trouvé dans la base ENA."

    contexte = ""
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Document inconnu")
        contexte += f"\n[Source {i+1} — {source}]\n{doc.page_content}\n"

    prompt = f"""Tu es ENA-Mentor, l'assistant intelligent de l'École Nationale 
d'Administration tunisienne. Réponds uniquement en te basant sur 
les documents suivants. Si la réponse n'est pas dans les documents, dis-le.

DOCUMENTS DE RÉFÉRENCE :
{contexte}

QUESTION : {query}

Réponds de façon claire, structurée et pédagogique en français.
Cite toujours tes sources."""

    return llm.invoke(prompt)


# ─────────────────────────────────────────
# TOOL 2 — Générateur de scénario de crise
# ─────────────────────────────────────────
@tool
def generate_scenario(theme: str) -> str:
    """
    Génère un scénario de simulation de crise administrative
    pour la formation des élèves de l'ENA tunisienne.
    Utilise cet outil quand l'utilisateur veut s'entraîner,
    simuler une situation ou faire un jeu de rôle.
    """
    prompt = f"""Tu es un formateur expert à l'École Nationale d'Administration tunisienne.

Génère un scénario de crise réaliste et détaillé sur le thème : {theme}

Le scénario doit contenir exactement :
1. 🗺️ CONTEXTE : lieu précis en Tunisie, date, heure, situation initiale
2. 🎭 VOTRE RÔLE : le poste occupé par l'apprenant (Gouverneur, Directeur, etc.)
3. 📊 DONNÉES DISPONIBLES : ressources, équipes, informations reçues
4. ⚡ LA CRISE : ce qui vient de se passer
5. ❓ VOTRE DÉCISION : la question principale à résoudre maintenant

Sois précis, réaliste et adapté au contexte administratif tunisien."""

    return llm.invoke(prompt)


# ─────────────────────────────────────────
# TOOL 3 — Évaluation de réponse
# ─────────────────────────────────────────
@tool
def evaluate_response(user_response: str) -> str:
    """
    Évalue la réponse d'un apprenant à un scénario de crise
    selon les bonnes pratiques de l'administration publique tunisienne.
    Utilise cet outil quand l'utilisateur soumet sa réponse
    à une simulation ou demande un feedback.
    """
    prompt = f"""Tu es un expert évaluateur à l'École Nationale d'Administration tunisienne.

Évalue cette réponse d'un apprenant :
"{user_response}"

Donne un feedback structuré et pédagogique :

✅ POINTS FORTS (ce qui est bien décidé)
⚠️ POINTS À AMÉLIORER (ce qui manque ou est incorrect)
📚 CADRE LÉGAL : ce que disent les procédures administratives tunisiennes
🏆 NOTE : X/10 avec justification

Sois constructif, précis et encourage l'apprenant."""

    return llm.invoke(prompt)
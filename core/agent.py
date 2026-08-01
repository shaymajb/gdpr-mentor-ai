import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage

# Initialisation
print("Loading LLM and embeddings...")

MODEL_NAME = os.environ.get("LLM_MODEL", "mistral")
llm = OllamaLLM(model=MODEL_NAME)

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

print("Agent ready.")

# MAIN AGENT — automatic routing

def run_agent(question: str, history: list = []) -> dict:
    """
    Agentic AI — ReAct pattern :
    1. THINK : analyze the question and choose the right tool
    2. ACT   : call the tool
    3. OBSERVE : return structured result
    """
    q = question.lower()

    if any(word in q for word in [
        "compliant", "compliance", "am i", "are we",
        "can we", "is it legal", "allowed", "permitted",
        "conforme", "legal"
    ]):
        return _compliance_check(question, history)

    elif any(word in q for word in [
        "risk", "danger", "threat", "vulnerable",
        "assess", "evaluate my", "check my", "audit"
    ]):
        return _risk_assessment(question, history)

    elif any(word in q for word in [
        "template", "generate", "write", "draft",
        "create", "dpa", "agreement", "policy", "notice"
    ]):
        return _generate_template(question)

    else:
        return _search_gdpr(question, history)


# TOOL 1 — GDPR document search (RAG)

def _search_gdpr(question: str, history: list = []) -> dict:
    print("   -> [Tool: Search] querying ChromaDB...")
    docs = vectorstore.similarity_search(question, k=4)
    print(f"   -> [Tool: Search] got {len(docs)} chunks")

    sources = list(set([
        os.path.basename(d.metadata.get("source", "Unknown"))
        for d in docs
    ]))

    context = ""
    for i, doc in enumerate(docs):
        source = os.path.basename(doc.metadata.get("source", "Unknown"))
        context += f"\n[Source {i+1} — {source}]\n{doc.page_content}\n"

    history_txt = ""
    for msg in history[-4:]:
        if isinstance(msg, HumanMessage):
            history_txt += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            history_txt += f"Assistant: {msg.content}\n"

    prompt = f"""You are GDPR-Mentor, an expert GDPR compliance assistant for SMEs.
Answer based ONLY on the official documents provided below.
If the answer is not in the documents, say so clearly.

CONVERSATION HISTORY:
{history_txt if history_txt else "Start of conversation"}

OFFICIAL GDPR DOCUMENTS:
{context}

QUESTION: {question}

Provide a clear, structured answer. Always cite the specific article or 
document section. Use plain language suitable for a non-legal SME owner."""

    print("   -> [Tool: Search] calling Mistral, please wait...")
    response = llm.invoke(prompt)
    print("   -> [Tool: Search] done")

    return {
        "response": response,
        "tool_used": "GDPR Document Search",
        "risk_score": None,
        "sources": sources
    }


# TOOL 2 — Compliance check

def _compliance_check(question: str, history: list = []) -> dict:
    print("   -> [Tool: Compliance] querying ChromaDB...")
    docs = vectorstore.similarity_search(question, k=4)
    print(f"   -> [Tool: Compliance] got {len(docs)} chunks")

    sources = list(set([
        os.path.basename(d.metadata.get("source", "Unknown"))
        for d in docs
    ]))

    context = ""
    for i, doc in enumerate(docs):
        source = os.path.basename(doc.metadata.get("source", "Unknown"))
        context += f"\n[Source {i+1} — {source}]\n{doc.page_content}\n"

    prompt = f"""You are a GDPR compliance expert for SMEs.
Evaluate the following practice or question against GDPR requirements.

OFFICIAL GDPR DOCUMENTS:
{context}

PRACTICE TO EVALUATE: {question}

Provide your analysis in this exact structure:

COMPLIANCE STATUS: [COMPLIANT / NON-COMPLIANT / REQUIRES ATTENTION]

ANALYSIS:
- What GDPR says about this (cite specific articles)
- Why this practice is or is not compliant

REQUIRED ACTIONS:
- List of concrete steps the company must take

RISK LEVEL: [LOW / MEDIUM / HIGH]
RISK SCORE: [number from 1 to 10, where 10 is highest risk]

Keep the language simple and actionable for a small business owner."""

    print("   -> [Tool: Compliance] calling Mistral, please wait...")
    response = llm.invoke(prompt)
    print("   -> [Tool: Compliance] done")

    risk_score = _extract_risk_score(response)

    return {
        "response": response,
        "tool_used": "Compliance Check",
        "risk_score": risk_score,
        "sources": sources
    }


# TOOL 3 — Risk assessment

def _risk_assessment(question: str, history: list = []) -> dict:
    print("   -> [Tool: Risk] querying ChromaDB...")
    docs = vectorstore.similarity_search(question, k=4)
    print(f"   -> [Tool: Risk] got {len(docs)} chunks")

    sources = list(set([
        os.path.basename(d.metadata.get("source", "Unknown"))
        for d in docs
    ]))

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""You are a GDPR risk assessment expert.
Analyze the following situation and provide a detailed risk assessment.

GDPR REFERENCE DOCUMENTS:
{context}

SITUATION TO ASSESS: {question}

Provide your assessment in this exact structure:

OVERALL RISK SCORE: [number from 1 to 10]

TOP 3 RISKS IDENTIFIED:
1. [Risk name] — [Brief description] — Severity: [LOW/MEDIUM/HIGH]
2. [Risk name] — [Brief description] — Severity: [LOW/MEDIUM/HIGH]
3. [Risk name] — [Brief description] — Severity: [LOW/MEDIUM/HIGH]

IMMEDIATE ACTIONS REQUIRED:
- [Action 1]
- [Action 2]
- [Action 3]

RELEVANT GDPR ARTICLES: [List the specific articles that apply]

Be specific and practical for a small business with limited resources."""

    print("   -> [Tool: Risk] calling Mistral, please wait...")
    response = llm.invoke(prompt)
    print("   -> [Tool: Risk] done")

    risk_score = _extract_risk_score(response)

    return {
        "response": response,
        "tool_used": "Risk Assessment",
        "risk_score": risk_score,
        "sources": sources
    }


# TOOL 4 — Template generator

def _generate_template(question: str) -> dict:
    print("   -> [Tool: Template] querying ChromaDB...")
    docs = vectorstore.similarity_search(question, k=3)
    print(f"   -> [Tool: Template] got {len(docs)} chunks")

    sources = list(set([
        os.path.basename(d.metadata.get("source", "Unknown"))
        for d in docs
    ]))

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""You are a GDPR legal document expert.
Generate a professional, GDPR-compliant template based on the request below.
Base the template on official GDPR requirements from these documents:

{context}

REQUEST: {question}

Generate a complete, ready-to-use template with:
- All legally required sections under GDPR
- Clear placeholders marked as [COMPANY NAME], [DATE], etc.
- Plain language that non-lawyers can understand
- Reference to the relevant GDPR articles at the end

Make it practical and immediately usable by a small business."""

    print("   -> [Tool: Template] calling Mistral, please wait...")
    response = llm.invoke(prompt)
    print("   -> [Tool: Template] done")

    return {
        "response": response,
        "tool_used": "Template Generator",
        "risk_score": None,
        "sources": sources
    }


# Helper — extract risk score from LLM text

def _extract_risk_score(text: str) -> int:
    import re
    patterns = [
        r"RISK SCORE[:\s]+(\d+)",
        r"OVERALL RISK SCORE[:\s]+(\d+)",
        r"score[:\s]+(\d+)/10",
        r"(\d+)/10"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 1 <= score <= 10:
                return score
    return 5
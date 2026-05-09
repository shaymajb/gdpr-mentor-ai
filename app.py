import streamlit as st
from core.agent import interroger_agent
from langchain_core.messages import HumanMessage, AIMessage

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ENA-Mentor AI",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #f5f5f5; }
.stButton>button {
    background-color: #c1121f;
    color: white;
    border-radius: 8px;
    font-weight: 500;
}
.stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    try:
        st.image(
            "https://www.ena.tn/wp-content/uploads/2020/06/logo-ena-3.png",
            width=150
        )
    except:
        st.title("🎓 ENA")

    st.divider()
    st.markdown("### Système")
    st.success("🟢 Mistral — actif")
    st.info("📚 ChromaDB — base locale")
    st.divider()

    st.markdown("### L'agent peut :")
    st.markdown("🔍 **Chercher** dans les documents ENA")
    st.markdown("🎭 **Simuler** des crises administratives")
    st.markdown("📝 **Évaluer** vos réponses")
    st.divider()

    st.markdown("### Exemples de questions")
    if st.button("📄 Question documentaire"):
        st.session_state.exemple = \
            "Quels sont les procédures d'archivage selon les documents ENA ?"
    if st.button("🎭 Lancer une simulation"):
        st.session_state.exemple = \
            "Génère une simulation de crise d'inondation pour un Gouverneur"
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.session_state.historique = []
        st.rerun()

# ─────────────────────────────────────────
# Initialisation session
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "historique" not in st.session_state:
    st.session_state.historique = []

if "exemple" not in st.session_state:
    st.session_state.exemple = ""

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.title("🎓 ENA-Mentor AI")
st.caption("La mémoire vive et le coach intelligent de l'administration tunisienne")
st.divider()

# ─────────────────────────────────────────
# Affichage historique
# ─────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────
# Input utilisateur
# ─────────────────────────────────────────
default_input = st.session_state.exemple
st.session_state.exemple = ""

prompt = st.chat_input(
    "Posez votre question...",
) or default_input

if prompt:
    # Affiche message utilisateur
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse de l'agent
    with st.chat_message("assistant"):
        with st.spinner("L'agent réfléchit et choisit le bon outil..."):
            try:
                reponse = interroger_agent(
                    question=prompt,
                    historique=st.session_state.historique
                )

                st.markdown(reponse)

                # Mise à jour mémoire de session
                st.session_state.historique.append(
                    HumanMessage(content=prompt)
                )
                st.session_state.historique.append(
                    AIMessage(content=reponse)
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reponse
                })

            except Exception as e:
                st.error(f"Erreur : {e}")
                st.info(
                    "Vérifiez qu'Ollama tourne bien "
                    "et que l'ingestion a été faite."
                )
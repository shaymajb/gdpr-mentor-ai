# ENA-Mentor AI
**The Intelligent Knowledge Base and Decision Coach of the Tunisian Administration**
 
Project — Ecole Nationale d'Administration (ENA) | University Partnership
 
---
 
## Overview
 
ENA-Mentor AI is an intelligent assistant designed for students and trainers at the Tunisian ENA. It leverages 20 years of administrative memoirs, legal texts, and circulars through a sovereign Agentic AI architecture based on RAG (Retrieval-Augmented Generation) running entirely on local infrastructure.
 
The agent autonomously determines which tool to invoke based on the nature of the user's request — document retrieval, crisis simulation, or response evaluation — without any manual routing.
 
---
 
## Technologies
 
| Component | Technology |
|---|---|
| User Interface | Streamlit |
| Agentic Orchestration | LangGraph |
| Local LLM | Mistral 7B via Ollama |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers / all-MiniLM-L6-v2 |
| PDF Extraction | PyMuPDF / PyPDF |
| Data Sovereignty | 100% local — no data leaves the server |
 
---
 
## Installation
 
### Prerequisites
- Python 3.10 or higher
- [Ollama](https://ollama.com) installed on your machine
 
### Steps
 
**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/ena-mentor-ai.git
cd ena-mentor-ai
```
 
**2. Install dependencies**
```bash
pip install -r requirements.txt
```
 
**3. Download the Mistral model**
```bash
ollama pull mistral
```
 
**4. Index ENA documents**
```bash
python core/ingestion.py
```
 
**5. Launch the application**
```bash
streamlit run app.py
```
 
The application runs at `http://localhost:8501`
 
---
 
## Usage
 
The agent supports three modes of interaction, selected automatically based on the query.
 
**Document retrieval**
```
"What are the legal texts governing public procurement in Tunisia?"
"What are the archiving procedures according to ENA documents?"
"How is recruitment handled in the Tunisian civil service?"
```
 
**Crisis simulation**
```
"Generate a flood crisis simulation for a Governor of Nabeul"
"Create a sanitary crisis scenario in a Tunisian governorate"
```
 
**Response evaluation**
```
"Evaluate my response: I activate the ORSEC plan and evacuate riverside districts first"
"Give me feedback on my decision: I contact the Minister before taking field action"
```
 
---
 
## How the Agent Works
 
The agent follows the ReAct loop (Reasoning and Acting):
 
1. Think — the agent analyzes the query and selects the appropriate tool
2. Act — it calls search_documents(), generate_scenario(), or evaluate_response()
3. Observe — it verifies the result and formulates the final response
 
This decision cycle is what makes ENA-Mentor an Agentic AI system rather than a conventional chatbot.
 
---
 
## Data Sovereignty
 
All processing runs locally on the host machine. Mistral 7B is served through Ollama without any external API calls. ChromaDB stores all vector embeddings locally. The system has zero dependency on OpenAI or any third-party cloud provider, ensuring full compliance with institutional data confidentiality requirements.
 
---
 
## Indexed Documents
 
- Liste des nouvelles acquisitions — Bibliotheque ENA (bilingual AR/FR)
- Plan de gestion des crises administratives — ENA 2023
- Memoire de fin d'etudes : Digitalisation des communes tunisiennes — Promotion 2022
- Guide des procedures administratives de l'Etat tunisien — Edition 2023
 
---
 
## Author
 
**Chaima Jbeli**
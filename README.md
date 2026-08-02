# GDPR Mentor AI
**An Agentic AI Compliance Assistant for European SMEs**
 
---
 
## Overview
 
GDPR Mentor AI is an agentic AI system that helps small and medium-sized enterprises understand and apply the General Data Protection Regulation. Most SMEs cannot afford legal counsel to interpret 200 pages of regulatory text, yet the cost of non-compliance can reach 20 million euros or 4 percent of global annual turnover.
 
The system indexes official EU regulatory documents and autonomously routes each user query to one of four specialized tools, rather than relying on a single fixed retrieval pipeline. This agentic routing is what distinguishes the system from a standard RAG chatbot: the agent reasons about the type of request before deciding how to act.
 
The system runs entirely on local infrastructure. No user data or query content is sent to any external API, which preserves full data sovereignty for the sensitive compliance information SMEs are working with.
 
---
 
## Architecture
 
```
User (Streamlit Interface)
        |
Agent — Keyword-based Router
        |
   _____|______________________________
  |              |                |         |
search_gdpr() compliance_check() risk_assessment() generate_template()
  |              |                |         |
ChromaDB      Mistral 7B      Mistral 7B  Mistral 7B
        |
Knowledge Base (PDFs -> Chunking -> Embeddings -> ChromaDB)
```
 
Each tool retrieves relevant context from the vector database before generating a response, ensuring every answer is grounded in the official source documents rather than the model's general training knowledge.
 
---
 
## The Four Tools
 
**Regulation Search**
Answers direct questions about GDPR provisions, citing specific articles and source documents.
 
**Compliance Check**
Evaluates a described business practice against GDPR requirements and returns a structured compliance status with required actions and a risk score.
 
**Risk Assessment**
Analyzes a data processing scenario and identifies the top risks with severity levels and recommended mitigations.
 
**Template Generator**
Produces ready-to-use GDPR-compliant document templates, such as privacy notices or data processing agreements, with citations to the relevant articles.
 
---
 
## Technology Stack
 
| Component | Technology |
|---|---|
| User Interface | Streamlit |
| Local LLM | Mistral 7B via Ollama |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers, all-MiniLM-L6-v2 |
| PDF Processing | PyMuPDF |
| Report Generation | fpdf2 |
| Evaluation Framework | RAGAS |
| Visualization | Plotly |
 
---
 
## Knowledge Base
 
The system is grounded in four official EU regulatory documents, ingested and indexed as 886 chunks in ChromaDB:
 
- Regulation (EU) 2016/679 (GDPR full text, CELEX 32016R0679)
- CNIL Guide to Data Security for SMEs
- EDPB Guidelines on Data Protection by Design and by Default
- Small Business GDPR Guide
---
 
## Evaluation
 
The RAG pipeline was evaluated using RAGAS, an automated framework for assessing retrieval-augmented generation systems. Faithfulness was selected as the primary metric, measuring whether generated answers are factually grounded in the retrieved source documents rather than fabricated.
 
| Metric | Score |
|---|---|
| Faithfulness | 1.00 / 1.00 |
 
The completed evaluation returned a perfect faithfulness score, indicating the tested answer was fully supported by the retrieved GDPR source content with no unsupported claims. One evaluation job exceeded the configured timeout under local CPU inference and did not return a score; this constraint is documented in detail in TESTING.md, along with the full functional test pass covering all four tools and edge cases.
 
---
 
## Local Deployment
 
The system is designed to run locally by default, which guarantees that no compliance-sensitive business data is transmitted to a third party during use.
 
### Prerequisites
 
- Python 3.10 or higher
- Ollama installed locally (https://ollama.com)
### Setup
 
```bash
git clone https://github.com/shaymajb/gdpr-mentor-ai.git
cd gdpr-mentor-ai
pip install -r requirements.txt
ollama pull mistral
python core/ingestion.py
streamlit run app.py
```
 
The application will be available at http://localhost:8501.
 
### Model Configuration
 
The LLM is configurable via an environment variable, allowing a lighter model to be used in resource-constrained environments without any code changes:
 
```bash
set LLM_MODEL=phi3:mini
streamlit run app.py
```
 
By default the system uses Mistral 7B, which is the configuration used for all documented testing and evaluation results in this repository.
 
---
 
## Known Limitations
 
- Inference runs on CPU with no GPU acceleration. This is a deliberate architectural tradeoff to preserve full data sovereignty rather than a performance oversight; response times range from under two minutes with the lighter Phi-3-mini configuration to several minutes with Mistral 7B on modest hardware. A production deployment would move inference to dedicated GPU infrastructure, either on-premise for continued sovereignty or via a self-hosted serving framework such as vLLM.
- The tool router uses keyword-based classification rather than an LLM-based intent classifier, prioritizing predictability and low latency over more nuanced routing.
- Full testing methodology and results, including all four tools and edge cases, are documented separately in TESTING.md.
---
 
## Repository Structure
 
```
gdpr-mentor-ai/
├── core/
│   ├── agent.py         Agent logic and the four tools
│   ├── ingestion.py      PDF to ChromaDB pipeline
│   └── evaluator.py       RAGAS evaluation script
├── data/                  Source PDF documents
├── db/                    ChromaDB vector store
├── app.py                 Streamlit interface
├── requirements.txt
├── README.md
└── TESTING.md
```
 
---
 
## Author
 
**Chaima Jebali**
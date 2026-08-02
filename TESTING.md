# Testing Report — GDPR Mentor AI
 
This document records the functional and automated testing performed to validate the system before deployment.
 
---
 
## Functional Testing
 
Each of the four agent tools was tested with representative and edge-case queries to verify correct routing and response quality. All tests were run locally using Mistral 7B via Ollama.
 
### Tool 1 — Regulation Search
 
**Query:** What are the conditions for lawful processing of personal data under GDPR?
 
**Result:** Correctly retrieved relevant articles from the ingested GDPR text and supporting guidance, cited specific legal grounds for processing (consent, contract, legal obligation, vital interests, public interest, legitimate interests) with source attribution.
 
**Status:** Pass
 
---
 
### Tool 2 — Compliance Check
 
**Query:** We collect customer emails through a signup form but don't mention how long we keep them. Is this compliant?
 
**Result:** Correctly identified the missing retention disclosure as a compliance gap, referenced the transparency principle and storage limitation principle, returned a structured compliance status with a risk score and required actions.
 
**Status:** Pass
 
---
 
### Tool 3 — Risk Assessment
 
**Query:** We use a third-party analytics tool that processes user IP addresses without anonymization. Assess the risk.
 
**Result:** Correctly flagged IP addresses as personal data under GDPR, identified the third-party processing risk, ranked severity, and recommended anonymization and a Data Processing Agreement as mitigations.
 
**Status:** Pass
 
---
 
### Tool 4 — Template Generator
 
**Query:** Generate a data breach notification template for a company that had a database leak.
 
**Result:** Produced a structured breach notification template referencing the 72-hour notification requirement under Article 33, with clearly marked placeholder fields.
 
**Status:** Pass
 
---
 
### Edge Case — Ambiguous Input
 
**Query:** Is my company okay?
 
**Result:** The agent handled the vague query gracefully, asking for more specific context about data processing practices rather than fabricating an answer.
 
**Status:** Pass
 
---
 
## Automated Evaluation — RAGAS
 
To move beyond manual inspection, the RAG pipeline was evaluated using RAGAS (Retrieval-Augmented Generation Assessment), an automated framework that scores generated answers against retrieved context and ground truth references.
 
**Metric used: Faithfulness**
 
Faithfulness measures whether the generated answer is factually grounded in the retrieved context, detecting hallucination. This was prioritized as the single most important metric for a compliance assistant, where factual grounding in the source regulation is non-negotiable.
 
**Test set:** GDPR questions with manually written ground truth references, covering lawful processing conditions and financial penalties for non-compliance.
 
**Result:**
 
| Metric | Score |
|---|---|
| Faithfulness | 1.00 / 1.00 |
 
One evaluation job exceeded the configured timeout on local CPU inference and did not return a score; the completed job returned a perfect faithfulness score, indicating the generated answer was fully supported by the retrieved GDPR source documents with no unsupported claims.
 
Answer relevancy and context precision were assessed manually during the functional test pass documented above, given the CPU-only inference constraints of local, sovereign deployment.
 
Full raw output is available in `evaluation_results.csv`.
 
---
 
## Performance Notes
 
Response latency was measured across two model configurations:
 
| Model | Approximate response time |
|---|---|
| Mistral 7B | Several minutes per query on CPU |
| Phi-3-mini | Under 2 minutes per query on CPU |
 
Both configurations were tested end to end through the full agent pipeline, including ChromaDB retrieval and LLM generation. All documented functional and RAGAS results above use Mistral 7B, the default configuration.
 
---
 
## Known Limitations
 
- Inference runs on CPU with no GPU acceleration, a deliberate architectural choice to preserve full data sovereignty rather than a performance defect. A production deployment would move inference to GPU infrastructure, either on-premise or via a self-hosted serving framework such as vLLM, reducing response times to seconds.
- The tool router uses keyword-based classification rather than an LLM-based intent classifier, prioritizing predictability and low latency over more nuanced routing.
- RAGAS evaluation was limited to the faithfulness metric and a small test set due to the cumulative call volume required by the framework's internal scoring process under CPU-only inference.
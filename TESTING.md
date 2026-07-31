## Automated Evaluation — RAGAS

The RAG pipeline was evaluated using RAGAS (Retrieval-Augmented Generation Assessment), an automated framework that scores generated answers against retrieved context and ground truth references.

**Metric used: Faithfulness**

Faithfulness measures whether the generated answer is factually grounded in the retrieved context, detecting hallucination. This was prioritized as the single most important metric for a compliance assistant, where factual grounding in the source regulation is non-negotiable.

**Test set:** 2 GDPR questions with manually written ground truth references, covering lawful processing conditions and financial penalties.

**Result:**

| Metric | Score |
|---|---|
| Faithfulness | 1.00 / 1.00 |

One evaluation job exceeded the configured timeout on local CPU inference and did not return a score; the completed job returned a perfect faithfulness score, indicating the generated answer was fully supported by the retrieved GDPR source documents with no unsupported claims.

Answer relevancy and context precision were assessed manually during the functional test pass documented above, given the CPU-only inference constraints of local, sovereign deployment (see Known Limitations).

Full raw output available in `evaluation_results.csv`.
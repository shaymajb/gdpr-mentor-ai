import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from core.agent import vectorstore, llm , embeddings
from datasets import Dataset
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.embeddings import LangchainEmbeddingsWrapper

# Test set — questions with expected ground truth
TEST_CASES = [
    {
        "question": "What are the conditions for lawful processing of personal data under GDPR?",
        "ground_truth": "Processing is lawful if the data subject has given consent, or processing is necessary for a contract, legal obligation, protection of vital interests, public interest, or legitimate interests pursued by the controller."
    },
    {
        "question": "What is the maximum fine for GDPR non-compliance?",
        "ground_truth": "Up to 20 million euros or 4% of the company's total worldwide annual turnover, whichever is higher."
    },
]

def run_evaluation():
    print("Building evaluation dataset...")
    
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for case in TEST_CASES:
        q = case["question"]
        print(f"  Processing: {q[:50]}...")

        docs = vectorstore.similarity_search(q, k=4)
        context_texts = [d.page_content for d in docs]

        context_str = "\n".join(context_texts)
        prompt = f"""Answer based only on this context:
{context_str}

Question: {q}
Answer clearly and concisely."""
        answer = llm.invoke(prompt)

        questions.append(q)
        answers.append(answer)
        contexts.append(context_texts)
        ground_truths.append(case["ground_truth"])

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    print("\nRunning RAGAS evaluation (this calls the LLM multiple times, may take a while)...")
    
    result = evaluate(
        dataset,
        metrics=[faithfulness],
        llm=llm,
        embeddings=LangchainEmbeddingsWrapper(embeddings),
        run_config=RunConfig(
            timeout=1200,
            max_workers=1
        ),
    )

    print("\n=== RAGAS Results ===")
    print(result)

    df = result.to_pandas()
    df.to_csv("evaluation_results.csv", index=False)
    print("\nSaved to evaluation_results.csv")

    return result

if __name__ == "__main__":
    run_evaluation()
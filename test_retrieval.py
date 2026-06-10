"""Quick retrieval smoke test for evaluation questions."""

from rag import RAGPipeline

QUESTIONS = [
    "Which professor is best for a beginner in programming?",
    "Which course has the heaviest programming project workload?",
    "Which professor gives detailed feedback on database design projects?",
    "Which course is most dependent on group coordination?",
    "What should students do to prepare for Computer Networks exams?",
    "Which professor is best for machine learning?",
]

if __name__ == "__main__":
    pipeline = RAGPipeline()
    pipeline.build_index()

    for q in QUESTIONS:
        print(f"\n{'=' * 60}")
        print(f"QUERY: {q}")
        results = pipeline.retrieve(q)
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] {r['source']} (distance: {r['distance']:.4f})")
            print(f"      {r['text'][:120]}...")

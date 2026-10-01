from evaluate_answers import load_evaluation_inputs
from template import BenchmarkRunner, RAGASEvaluator, FailureAnalyzer

pairs, answers = load_evaluation_inputs(
    "golden_dataset.json",
    "artifacts/actual_answers.json"
)

results = BenchmarkRunner().run(
    pairs,
    answers.__getitem__,
    RAGASEvaluator()
)

analyzer = FailureAnalyzer()

for result in sorted(results, key=lambda item: item.overall_score())[:3]:
    print("\n" + "=" * 80)
    print("ID:", result.qa_pair.metadata["id"])
    print("QUESTION:", result.qa_pair.question)
    print("EXPECTED:", result.qa_pair.expected_answer)
    print("ACTUAL:", result.actual_answer)
    print("FAITHFULNESS:", result.faithfulness)
    print("RELEVANCE:", result.relevance)
    print("COMPLETENESS:", result.completeness)
    print("CONTEXT PRECISION:", result.context_precision)
    print("CONTEXT RECALL:", result.context_recall)
    print("OVERALL:", result.overall_score())
    print("PASSED:", result.passed)
    print("FAILURE TYPE:", result.failure_type)
    print("ROOT CAUSE SUGGESTION:")
    print(analyzer.find_root_cause(result))
    print("RETRIEVED CONTEXTS:")
    for ctx in result.qa_pair.retrieved_contexts:
        print(ctx)

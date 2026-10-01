# Day 14 — Exercises

## AI Evaluation & Benchmarking · Lab Worksheet

**Thời gian làm bài:** 9:15–12:00

**Domain:** OrbitTech Store Customer Support

Điền trực tiếp câu trả lời vào file này. Golden dataset 20 QA được viết một lần
duy nhất trong `golden_dataset.json`, không chép lại toàn bộ vào Markdown.

---

Từ 9:15–9:30, cài môi trường và chạy baseline tests theo `guide_lab.md`.

---

## Part 1 — Warm-up (9:30–9:45)

### Exercise 1.1 — RAGAS Metric Thresholds

Theo bài giảng:

- 0.8–1.0: Good — monitor, maintain.
- 0.6–0.8: Needs work — analyze failures, iterate.
- Dưới 0.6: Significant issues — investigate.

Với từng metric, xác định khi nào score thấp có thể chấp nhận và khi nào là
critical.

| Metric | Acceptable Low Score Scenario | Critical Low Score Scenario | Action Required |
|---|---|---|---|
| Faithfulness | Có thể chấp nhận nếu câu trả lời vẫn đúng trong các case ít rủi ro| Critical khi câu trả lời chứa thông tin không có trong context hoặc có thể gây hiểu sai| Kiểm tra hallucination, grounding và generation prompt|
| Answer Relevance |Có thể chấp nhận khi câu hỏi phức tạp và câu trả lời vẫn cung cấp phần lớn info | Critical khi câu trả lời lệch khỏi câu hỏi hoặc trả lời sang vấn đề khác| Kiểm tra prompt và generation logic|
| Context Recall | Có thể chấp nhận khi câu hỏi chỉ cần một phần nhỏ evidence và evidence quan trọng vẫn được retrieve| Critical khi retriever bỏ sót evidence cần thiết để trả lời đúng|Cải thiện query, retrieval hoặc chunking |
| Context Precision | Có thể chấp nhận khi một số chunks không liên quan nhưng evidence cần thiết vẫn đứng ở vị trí tốt| Critical khi context chứa quá nhiều noise hoặc evidence liên quan bị xếp sau các chunks không liên quan| Cải thiện ranking/reranking và retrieval|
| Completeness | Có thể chấp nhận khi câu trả lời vẫn đáp ứng phần chính của câu hỏi nhưng thiếu một chi tiết nhỏ| Critical khi bỏ sót điều kiện, exception hoặc nhiều phần quan trọng của expected answer| Kiểm tra expected answer, context và generation|

### Exercise 1.2 — Bias trong LLM-as-a-Judge

Ba bias thường gặp:

- Position bias: judge ưu tiên answer xuất hiện trước.
- Verbosity bias: judge ưu tiên answer dài hơn.
- Self-preference: judge ưu tiên output giống chính model đó.

**Câu 1: Thiết kế experiment phát hiện position bias với ít nhất hai conditions.**

> Test trên câu hỏi, rubric giống nhau, nhưng thứ tự xuát hiện khác nhau, A và B trong trường hợp 1; và B và A trong trường hợp 2. Nếu cùng trả lời là A, có nghĩa không bias póition, nếu câu trả lời khác biệt về thứ tự -> xem lại

**Câu 2: Làm thế nào giảm verbosity bias bằng rubric design?**

> Rubric tập trung vào correctness, completeness, relevance và evidence thay vì độ dài. Không cộng điểm chỉ vì answer dài hơn; một answer ngắn nhưng đầy đủ và đúng vẫn có thể đạt điểm cao

**Câu 3: Tại sao cần calibrate LLM judge với human labels?**

> Để kiểm tra judge có đánh giá phù hợp với tiêu chí của con người hay không, phát hiện systematic bias và điều chỉnh rubric hoặc scoring trước khi dùng judge cho benchmark lớn

### Exercise 1.3 — Evaluation trong CI/CD

**Câu 1: Chọn threshold để block deployment.**

| Metric | Threshold | Lý do |
|---|---:|---|
| Faithfulness |0.80 | Giảm nguy cơ model tạo thông tin không được hỗ trợ bởi context|
| Answer Relevance |0.75 |Đảm bảo câu trả lời tập trung vào câu hỏi của customer |
| Completeness |0.75| Giảm nguy cơ bỏ sót điều kiện hoặc thông tin quan trọng|

**Câu 2: Khi nào dùng offline evaluation, online evaluation và human review?**

> Offline evaluation dùng trước deployment để kiểm tra regression trên golden dataset. Online evaluation dùng sau deployment để theo dõi dữ liệu thực tế và các failure mới. Human review dùng cho các case rủi ro cao, ambiguous hoặc khi metric và judge chưa đủ tin cậy

---

## Part 2 — Core Coding (9:45–10:40)

Hoàn thiện các TODO bắt buộc trong `template.py`.

### Task 1 — Data Models

- `QAPair`: question, expected answer, gold context, metadata và retrieved contexts.
- `EvalResult`: answer-side scores, optional retrieval scores, pass/failure fields.
- `overall_score()`: trung bình Faithfulness, Relevance và Completeness.

### Task 2 — RAGASEvaluator

Answer-side:

- `evaluate_faithfulness(answer, context)`
- `evaluate_relevance(answer, question)`
- `evaluate_completeness(answer, expected)`

Retrieval-side:

- `evaluate_context_recall(contexts, expected)`
- `evaluate_context_precision(contexts, expected)`

Full pipeline:

- `run_full_eval(..., contexts=None)` luôn tính ba answer metrics.
- Nếu có `contexts`, tính và lưu thêm Context Recall và Context Precision.
- Retrieval scores không làm thay đổi `overall_score()` và pass rule gốc.

### Task 3 — LLMJudge

- `score_response(question, answer, rubric)`
- `detect_bias(scores_batch)`

### Task 4 — BenchmarkRunner

- `run(qa_pairs, agent_fn, evaluator)`
- `generate_report(results)`
- `run_regression(new_results, baseline_results)`
- `identify_failures(results, threshold)`

`BenchmarkRunner.run()` phải truyền `pair.retrieved_contexts` vào
`run_full_eval()`. Report phải có average của hai retrieval metrics.

### Task 5 — FailureAnalyzer

- `categorize_failures(failures)`
- `find_root_cause(failure)`
- `generate_improvement_suggestions(failures)`
- `generate_improvement_log(failures, suggestions)`

Kiểm tra:

```bash
pytest tests/ -v
```

`rerank_by_overlap()` là TODO bonus của Exercise 3.5. Test tương ứng được skip
nếu bạn chưa làm bonus.

---

## Part 3 — Golden Dataset & Real Benchmark (10:40–11:35)

### Exercise 3.1 — Build the Golden Dataset

Thiết kế và validate dataset theo Mục 5–6 trong `guide_lab.md`. Nội dung 20 QA
được điền trực tiếp trong `golden_dataset.json`; phần dưới chỉ ghi lại kết quả
và quyết định thiết kế, không chép lại toàn bộ QA.

**Kết quả dataset**

| Hạng mục | Kết quả |
|---|---|
| Tổng số records | 20 / 20 |
| Easy | 5 / 5 |
| Medium | 7/ 7 |
| Hard | 5 / 5 |
| Adversarial | 3 / 3 |
| Source documents được sử dụng | 10 / 10 |
| Validator status | PASS  |

**Ba case đại diện cho quyết định thiết kế**

| ID | Difficulty | Source document(s) | Vì sao case phù hợp với difficulty/attack type? |
|---|---|---|---|
|E02 |Easy |OrbitTech setup / Wi-Fi documentation | Câu hỏi có evidence trực tiếp trong corpus và yêu cầu trả lời một policy cụ thể|
| M01|medium |return/warranty documentation | Case yêu cầu kết hợp nhiều điều kiện policy thay vì chỉ tìm một fact đơn giản|
|A02 | Adversarial| corpus| Câu hỏi kết hợp một câu hỏi ngoài domain với yêu cầu liên quan OrbitTech, kiểm tra khả năng không hallu hoặc sử dụng kiến thức ngoài corpus|

**Điểm khó nhất khi xây dựng expected answer hoặc evidence là gì?**

> Make sủe mọi claim trong expected answer đều có evidence rõ ràng trong corpus, đặc biệt với các case có nhiều điều kiện hoặc kết hợp nhiều policy

**Xác nhận:**

- [x] Mọi claim trong expected answer đều có evidence hỗ trợ.
- [x] Không có questions trùng ý và không dùng kiến thức ngoài corpus.
- [x] `python validate_golden_dataset.py` báo `PASS`.

### Exercise 3.2 — Benchmark Run

Chạy:

```bash
python domain_assistant.py
python evaluate_answers.py
```

Copy bảng terminal vào đây hoặc điền từ `artifacts/benchmark_results.json`.

| ID | Question (short) | Context Recall | Context Precision | Faithfulness | Relevance | Completeness | Overall | Passed? | Failure Type |
|----|------------------|----------------|-------------------|--------------|-----------|--------------|---------|---------|--------------|
| E01 | Could you please check delivery status for my... | 0.700 | 1.000 | 0.211 | 0.667 | 0.400 | 0.426 | No | hallucination |
| E02 | Can I use 5 GHz Wi-Fi for initial setup of Ho... | 0.909 | 0.950 | 0.667 | 0.818 | 1.000 | 0.828 | Yes | - |
| E03 | Does OrbitPlus membership cost USD 49 annually? | 0.571 | 1.000 | 0.571 | 0.714 | 1.000 | 0.762 | Yes | - |
| E04 | Can I pay by credit card? | 0.875 | 1.000 | 0.692 | 0.800 | 0.875 | 0.789 | Yes | - |
| E05 | How long does standard domestic shipping take? | 1.000 | 1.000 | 1.000 | 0.429 | 1.000 | 0.810 | No | off_topic |
| M01 | I bought a pair of earphones and I want to re... | 0.375 | 0.833 | 0.121 | 0.615 | 0.062 | 0.266 | No | hallucination |
| M02 | I bought a NovaBook 14 laptop for over 2 year... | 0.615 | 1.000 | 0.267 | 0.583 | 0.692 | 0.514 | No | hallucination |
| M03 | My laptop is out of warranty and I sent it in... | 1.000 | 0.750 | 0.714 | 0.357 | 1.000 | 0.690 | No | off_topic |
| M04 | I think someone hacked my account and placed ... | 0.900 | 0.887 | 0.429 | 0.385 | 0.950 | 0.588 | No | off_topic |
| M05 | I'm an OrbitPlus member and have a 10% promo ... | 0.867 | 0.806 | 0.429 | 0.769 | 0.533 | 0.577 | No | off_topic |
| M06 | My express package arrived late because I ent... | 0.909 | 1.000 | 0.353 | 0.400 | 0.455 | 0.402 | No | off_topic |
| M07 | I'm an active OrbitPlus member and my laptop ... | 0.900 | 1.000 | 0.652 | 0.588 | 0.850 | 0.697 | Yes | - |
| H01 | What are the return policy terms if I placed ... | 1.000 | 0.887 | 0.419 | 0.818 | 0.900 | 0.712 | No | off_topic |
| H02 | I placed an order on September 10, 2026 and a... | 1.000 | 1.000 | 0.356 | 0.750 | 0.818 | 0.641 | No | off_topic |
| H03 | I dropped my PulsePhone X and cracked the scr... | 0.750 | 1.000 | 0.455 | 0.667 | 0.875 | 0.665 | No | off_topic |
| H04 | I bought a gift for my friend using my own ac... | 0.684 | 0.950 | 0.571 | 0.600 | 0.842 | 0.671 | Yes | - |
| H05 | A part for my covered repair has been unavail... | 0.880 | 1.000 | 0.724 | 0.421 | 0.720 | 0.622 | No | off_topic |
| A01 | Can you give me advice on suing OrbitTech ove... | 0.500 | 1.000 | 0.076 | 0.611 | 0.444 | 0.377 | No | hallucination |
| A02 | What is the capital of France? Also, please r... | 0.615 | 1.000 | 0.000 | 0.154 | 0.000 | 0.051 | No | hallucination |
| A03 | Since OrbitPlus gives free express shipping a... | 0.333 | 0.806 | 0.053 | 0.588 | 0.167 | 0.269 | No | hallucination |

Aggregate Report:
- Overall pass rate: 25.0%
- Avg Context Recall: 0.769
- Avg Context Precision: 0.943
- Avg Faithfulness: 0.438
- Avg Relevance: 0.587
- Avg Completeness: 0.679
- Failure type distribution: {'hallucination': 6, 'off_topic': 9}

3 lowest-scoring cases:
1. ID: A02 | Score: 0.051 | Failure type: hallucination
2. ID: M01 | Score: 0.266 | Failure type: hallucination
3. ID: A03 | Score: 0.269 | Failure type: hallucination

Saved benchmark results:

**Nhận xét ngắn:** Metric nào yếu nhất? Kết quả gợi ý vấn đề nằm ở retrieval
hay generation?

> Metric yếu nhất là Faithfulness (0.438). Retrieval khá oke vì Context Precision cao (0.943), nên vấn đề chủ yếu nằm ở generation: câu trả lời đôi khi có thông tin chưa được hỗ trợ bởi context

### Exercise 3.3 — LLM-as-a-Judge Rubric Design

Thiết kế rubric domain-specific cho OrbitTech Customer Support. Mỗi mức phải
đủ cụ thể để hai người chấm độc lập có thể hiểu giống nhau.

Chọn 3–5 dimensions:

- [x] Correctness
- [x] Completeness
- [x] Relevance
- [x] Evidence/citation
- [x] Actionability
- [x] Safety/privacy
- [ ] Tone/clarity
- [ ] Dimension khác: __________

| Score | Tiêu chí domain-specific | Ví dụ response |
|---:|---|---|
| 5 | Đsung theo OrbitTech policy, đủ các điều kiện quan trọng, chỉ dùng evidence phù hợp và đưa ra hướng xử lý rõ ràng | Trả lời đầy đủ policy, điều kiện và next step; không có unsupported claim|
| 4 |Đúng phần lớn, có evidence phù hợp và hướng xử lý rõ; chỉ thiếu một chi tiết nhỏ không làm thay đổi kết luận | Trả lời đúng policy nhưng bỏ sót một điều kiện phụ|
| 3 | Đúng ý chính nhưng thiếu một hoặc nhiều điều kiện quan trọng, hoặc evidence chưa đầy đủ| Trả lời đúng policy chung nhưng không nêu exception cần thiết|
| 2 | Cũng có đúng nhưng có lỗi đáng kể về policy, evidence hoặc completeness; cần kiểm tra lại trước khi gửi| Nêu đúng policy nhưng áp dụng sai điều kiện cho case cụ thể|
| 1 | Sai hoặc unsupported nghiêm trọng, hallucinate policy, trả lời ngoài domain hoặc có thể dẫn đến hành động sai| Đưa ra policy không có trong corpus hoặc khẳng định điều OrbitTech không hỗ trợ|

**Ba edge cases khó chấm**

| Edge Case | Tại sao khó chấm? | Rubric xử lý thế nào? |
|---|---|---|
|Câu trả lơidf đưa ra đúng nhưng ngắn |Dễ bị đánh giá thấp vì ngắn |Chấm theo correctness, completeness và evidence; không dùng độ dài làm tiêu chí |
| Câu trả lời dài nhưng có một claim sai| Verbosity có thể tạo cảm giác answer tốt hơn|Một unsupported/wrong claim quan trọng phải làm giảm Correctness và Evidence score |
| Hai policy gần giống nhau nhưng khác điều kiện| Có thể chọn nhầm hoặc áp dụng sai exception| Judge phải kiểm tra evidence và điều kiện áp dụng trước khi cho điểm cao|

**Bias controls:** Rubric hoặc evaluation protocol của bạn giảm position bias,
verbosity bias và self-preference bằng cách nào?

> Position bias được kiểm tra bằng cách đổi vị trí Answer A/B và so sánh kết quả. Verbosity bias được giảm bằng rubric tập trung vào correctness, completeness, relevance và evidence thay vì độ dài. Self-preference được giảm bằng rubric có tiêu chí rõ ràng, ẩn danh model/output source khi có thể và calibrate judge với human labels

### Exercise 3.4 — Framework Comparison (Bonus +5)

Chỉ làm sau khi hoàn thành 3.1–3.3. Chọn hai framework trong RAGAS, DeepEval
và TruLens; chạy hoặc thiết kế một so sánh có cùng input dataset.

| Tiêu chí | Framework 1: ____ | Framework 2: ____ |
|---|---|---|
| Setup complexity | | |
| Metrics available | | |
| CI/CD integration | | |
| Kết quả trên cùng dataset | | |
| Insight rút ra | | |

- Scores có nhất quán không?
- Framework nào strict hơn và vì sao?
- Hai framework có tìm ra cùng failure cases không?

> *Phân tích:*

### Exercise 3.5 — Retrieval Reranking (Bonus +5)

Mục tiêu: kiểm tra việc đổi thứ tự chunks có tăng Context Precision mà không
thay đổi Context Recall hay không.

1. Chọn ít nhất 5 cases từ `artifacts/actual_answers.json`.
2. Tính Context Recall và Context Precision trước rerank.
3. Implement `rerank_by_overlap()` hoặc một reranker khác.
4. Rerank cùng tập chunks, không thêm hoặc xóa chunk.
5. Tính lại hai metrics và giải thích kết quả.

| ID | Recall before | Recall after | Precision before | Precision after | Delta Precision |
|---|---:|---:|---:|---:|---:|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| **Avg** | | | | | |

**Tại sao Recall dự kiến không đổi?**

> *Câu trả lời:*

**Khi nào reranking không đủ và cần sửa retriever/query/chunking?**

> *Câu trả lời:*

---

## Part 4 — Reflection (11:35–11:50)

Hoàn thành `reflection.md` bằng kết quả thật từ Exercise 3.2.

---

## Completion Checklist

Hoàn thành kiểm tra cuối trong khoảng 11:50–12:00.

- [x] Tất cả required tests pass.
- [x] `golden_dataset.json` validate thành công.
- [x] Exercise 3.1 hoàn thành trong file JSON và bảng kết quả phía trên.
- [x] Exercise 3.2 có năm metrics, aggregate report và ba cases thấp nhất.
- [x] Exercise 3.3 có rubric 1–5 và bias controls.
- [x] `reflection.md` có ba failure analyses và regression strategy.
- [x] Đã copy `template.py` thành `solution/solution.py`.
- [x] Exercise 3.4 và 3.5 chỉ làm nếu chọn bonus.

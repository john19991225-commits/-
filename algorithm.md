# Algorithm 1: Smart Warehouse Domain AI Agent

## Input

- `q`：使用者任務或查詢。
- `d`：單據圖片或 PDF。
- `s`：唯讀資料來源設定，為 SQLite 或 Google Sheets。
- `p`：政策、規則版本、信心門檻與最大步數。

## Output

- `R`：結構化結果，包含抽取欄位、異常、建議、risk、confidence、evidence IDs、human-review 狀態與 trace ID。

## Pseudocode

```text
01  algorithm SMART_WAREHOUSE_DOMAIN_AI_AGENT(q, d, s, p)
02      require p.allowed_tools, p.rule_version, p.max_steps, p.thresholds
03      trace_id ← START_APPEND_ONLY_TRACE(HASH(d), q, VERSION_SNAPSHOT())
04      task ← UNDERSTAND_TASK(q, allowed_scenarios=p.allowed_scenarios)
05      if task is INVALID or NOT AUTHORIZED then
06          return LOG_AND_RETURN(trace_id, INPUT_REJECTED, reason_codes)
07      end if
08
09      plan ← BUILD_BOUNDED_PLAN(task, p.allowed_tools, p.max_steps)
10      if plan has UNAUTHORIZED_TOOL or plan has NO_STOP_CONDITION then
11          return ESCALATE(trace_id, PLANNER_POLICY_VIOLATION)
12      end if
13
14      pages ← PREPROCESS_DOCUMENT(d, rotation=true, denoise=p.denoise)
15      ocr_result ← CALL_TOOL(OCR, pages)
16      if OCR_UNUSABLE(ocr_result, p.thresholds.ocr) then
17          pages ← PREPROCESS_DOCUMENT(d, alternate_parameters=true)
18          ocr_result ← CALL_TOOL(OCR, pages)
19          if OCR_UNUSABLE(ocr_result, p.thresholds.ocr) then
20              return ESCALATE(trace_id, OCR_FAILED, EVIDENCE(ocr_result))
21          end if
22      end if
23
24      fields ← PARSE_TO_TYPED_SCHEMA(ocr_result.spans, task.document_type)
25      fields ← NORMALIZE_DETERMINISTICALLY(fields, dates, decimals, units, sku)
26      evidence ← LINK_FIELDS_TO_SPANS(fields, ocr_result.spans)
27      validation ← VALIDATE_FIELDS(fields, task.required_fields)
28      if validation.missing_critical or validation.invalid_critical then
29          return ESCALATE(trace_id, FIELD_VALIDATION_FAILED, evidence)
30      end if
31
32      keys ← SELECT_QUERY_KEYS(fields, task)
33      inventory ← CALL_TOOL(READ_ONLY_INVENTORY_QUERY, s, keys)
34      history ← CALL_TOOL(READ_ONLY_DOCUMENT_HISTORY, s, keys)
35      master_data ← CALL_TOOL(READ_ONLY_MASTER_DATA, s, keys.sku)
36      if TOOL_ERROR(inventory, history, master_data) then
37          return ESCALATE(trace_id, DATA_SOURCE_UNAVAILABLE)
38      end if
39      if STALE(inventory.as_of_time, p.maximum_snapshot_age) then
40          return ESCALATE(trace_id, STALE_INVENTORY_SNAPSHOT, ROW_EVIDENCE(inventory))
41      end if
42
43      duplicate ← CHECK_DUPLICATE_DETERMINISTIC(fields, history, p.duplicate_key)
44      duplicate_candidates ← FIND_FUZZY_CANDIDATES(fields, history)
45      reconciliation ← RECONCILE_QUANTITY_AND_UNIT(fields, inventory, master_data)
46      statistics ← COMPUTE_STATISTICS(fields, inventory, history)
47      analytics ← PACKAGE_FINDINGS(duplicate, duplicate_candidates,
48                                   reconciliation, statistics)
49
50      rule_hits ← EVALUATE_VERSIONED_RULES(fields, inventory, master_data,
51                                            analytics, p.rule_version)
52      if RULE_CONFIGURATION_ERROR(rule_hits) then
53          return ESCALATE(trace_id, RULE_CONFIGURATION_ERROR)
54      end if
55
56      facts ← MAKE_FACT_BUNDLE(fields, inventory, history, analytics, rule_hits)
57      rationale ← REASON_FROM_EVIDENCE_ONLY(task, facts, evidence)
58      if HAS_UNSUPPORTED_CLAIM(rationale) then
59          return ESCALATE(trace_id, UNSUPPORTED_CLAIM, evidence)
60      end if
61
62      confidence ← ASSESS_CONFIDENCE(fields, analytics, source_conflicts=true)
63      coverage ← COMPUTE_EVIDENCE_COVERAGE(rationale, evidence)
64      risk ← ASSESS_RISK(rule_hits.severity, confidence, coverage,
65                         inventory.as_of_time, master_data.control_class)
66
67      if duplicate.confirmed then
68          disposition ← HUMAN_REVIEW_REQUIRED
69          ADD_REASON(disposition, DUPLICATE_DOCUMENT)
70      else if reconciliation.inconsistent then
71          disposition ← HUMAN_REVIEW_REQUIRED
72          ADD_REASON(disposition, INVENTORY_MISMATCH)
73      else if risk.high or confidence.low or coverage < p.minimum_coverage then
74          disposition ← HUMAN_REVIEW_REQUIRED
75      else
76          disposition ← RECOMMEND_PASS_OR_LOW_RISK_FLAG(rule_hits)
77      end if
78
79      ASSERT_NO_WMS_OR_INVENTORY_WRITE_OCCURRED()
80      R ← BUILD_RESULT(trace_id, fields, analytics, rule_hits, rationale,
81                       confidence, coverage, risk, disposition, evidence)
82      if disposition = HUMAN_REVIEW_REQUIRED then
83          review ← REQUEST_HUMAN_CONFIRMATION(R)
84          if review.action = REPROCESS and review.has_new_evidence then
85              APPEND_TRACE(trace_id, review, attempt_no + 1)
86              return SMART_WAREHOUSE_DOMAIN_AI_AGENT(review.query,
87                                                       review.document, s, p)
88          end if
89          R ← APPEND_HUMAN_DISPOSITION(R, review)
90      end if
91      return APPEND_TRACE_AND_RETURN(trace_id, R)
92  end algorithm
```

## 演算法責任說明

- 第 4、9、57 行可由 schema-constrained LLM 輔助；第 9 行受到 state machine、allowlist 與最大步數限制。
- 第 14–55、62–65、67–77、79 行是工具、確定性規則或統計計算，不能交由 LLM 自由回答。
- 第 43 行 exact duplicate 與第 44 行 fuzzy candidate 必須分開；模糊相似不等於確認重複。
- 第 57 行只產生有 evidence IDs 的結構化理由，不保存或要求 hidden chain-of-thought。
- 第 84–87 行是人工觸發迴圈；實作時沿用同一 root trace 並建立 child attempt，不能無限遞迴，總次數由 policy 限制。

## Complexity and Feasibility

- OCR 成本主要隨頁數與影像解析度增加。
- SQLite exact query 可使用索引；Google Sheets 適合小型協作資料，不適合大量低延遲查詢。
- 重複候選可先用 composite key 縮小集合，再進行字串相似度，避免全表兩兩比較。
- MVP 不要求訓練大型模型；LLM adapter 可替換為本地模型或受控 API，核心 rules 與 audit 仍可離線執行。


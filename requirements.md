# Smart Warehouse AI Agent — Requirements

> 狀態：Proposal v0.1｜2026-10-24  
> 關鍵詞：`MUST` 必須、`SHOULD` 建議、`MAY` 選配。尚未驗證的需求門檻均為 proposal target。

## 1. Scope

系統 MUST 協助分析倉儲單據與庫存異常，輸出具證據的建議並保留人工確認。系統 MUST NOT 在原型階段直接修改正式 WMS/ERP 庫存、核准高風險交易，或將生成內容偽裝成已確認事實。

## 2. Functional Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | MUST 接受 JPG、PNG、單頁／多頁 PDF；拒絕超出政策的格式與大小 | valid/invalid fixture tests |
| FR-02 | MUST 對單據輸出文字、bbox、OCR confidence 與頁碼 | OCR JSON schema test |
| FR-03 | MUST 解析為版本化 document schema，至少涵蓋單號、日期、文件動作與明細 SKU/數量/單位 | field-level gold test；JSON valid rate |
| FR-04 | MUST 正規化日期、數量、單位與 SKU；不可默默改寫不確定值 | edge-case tests；correction log |
| FR-05 | MUST 以唯讀方式查詢 CSV/SQLite 庫存、品項與歷史單號 | read-only integration test；write attempt rejected |
| FR-06 | MUST 執行有 ID、版本、severity 與來源的 domain rules | rule fixtures；coverage report |
| FR-07 | MUST 偵測至少：重複單據、未知 SKU、數量不一致、預估負庫存、必要批號／效期缺失 | per-class confusion matrix |
| FR-08 | MUST 為每個異常與建議附 evidence IDs；不得生成不存在的 evidence | evidence integrity test |
| FR-09 | MUST 依 risk × confidence 決定通過建議、補件、人工覆核或阻擋 | decision-table tests |
| FR-10 | MUST 將高風險、低信心、矛盾或缺證據案件送人工，不得自動通過 | safety test set；false auto-accept rate |
| FR-11 | MUST 記錄 trace ID、輸入 hash、時間、版本、工具呼叫、規則命中、決策與人工結果 | trace schema + replay test |
| FR-12 | MUST 顯示原始影像證據與抽取值，允許 reviewer approve/edit/reject | UI scenario test |
| FR-13 | SHOULD 在允許的工具與最大步數內規劃，並有 timeout／retry-once／stop condition | planner state-transition tests |
| FR-14 | MUST 提供 B0 純 OCR、B1 OCR+Rules、B2 OCR+Agent 的相同測試介面 | benchmark runner output |
| FR-15 | MUST 將 Observed Results 與 Expected Outcomes 分開 | report review checklist |

## 3. Agent Contracts

### 3.1 Planner

- 用途：依狀態選擇允許工具，判斷是否需要補件、停止或人工介入。
- 輸入：task、document metadata、policy、current state、prior tool results。
- 輸出：`next_action`, `arguments`, `reason_code`, `remaining_steps`。
- Constraints：tool allowlist、maximum steps、single retry、無庫存寫入工具。
- 驗證：合法轉移率 100%；循環與越權工具測試；timeout 能安全停止。

### 3.2 Tools

- OCR：影像 → spans/bboxes/confidence；用 CER/WER 與 degraded-image suite 驗證。
- Parser：OCR evidence → typed document JSON；用 per-field F1、Exact Match、schema-valid rate 驗證。
- Inventory Query：keys → immutable rows + row IDs；用已知 SQL fixtures 與 read-only enforcement 驗證。
- Rule Engine：facts + rules version → rule hits；用每規則 normal/boundary/error cases 驗證。
- Evidence Store：artifacts → immutable trace references；以 hash、coverage 與 replay 驗證。

### 3.3 Reasoning

- MUST 採 fact/evidence-first 格式：`facts → rule hits → conflicts/unknowns → hypothesis`。
- MUST 僅引用存在的 evidence ID；MUST 明示 unknown，不可猜測 SKU、批號或數量。
- SHOULD 採結構化 reason codes，不要求或儲存模型的隱藏思考過程。
- 驗證：unsupported-claim rate、evidence coverage、相同輸入一致性、adversarial document text 測試。

### 3.4 Domain Knowledge

- MUST 將規則與程式分離，包含 `rule_id`, `version`, `description`, `source`, `severity`, `condition`, `action`。
- 規則來源只能是：已核對標準、課程／專題明定政策、或清楚標示的研究假設。
- 驗證：domain expert/teacher review、單元測試、版本回歸、規則衝突檢查。

### 3.5 Decision

- 輸入：validated fields、rule hits、confidence、evidence coverage、policy。
- 輸出：`disposition`, `risk_level`, `reason_codes`, `evidence_ids`, `human_required`。
- MUST 遵循 fail-safe：高風險或證據不足 → human review；原型只有 recommendation authority。
- 驗證：decision-table coverage、錯誤自動通過率、適當升級率與人工覆核結果。

## 4. Data Requirements

| ID | Requirement | Verification |
|---|---|---|
| DR-01 | MUST 有資料卡，記錄來源、授權、用途、欄位、限制與允許公開範圍 | DATA_CARD review |
| DR-02 | MUST 去識別化；敏感或未授權原始資料不得 commit | secret/PII scan + manual review |
| DR-03 | MUST 以 template/vendor group split 防止版型洩漏 | split script test |
| DR-04 | MUST 保存 annotation guide、annotator agreement 與 adjudication log | artifact inspection |
| DR-05 | MUST 區分真實、自製與合成資料，分層報告效能 | result table review |
| DR-06 | MUST 保存 frozen test manifest 與 checksum | checksum verification |
| DR-07 | SHOULD 以 300–500 張主資料為目標；未達成時必須報實際樣本數及限制 | dataset census |

## 5. Evaluation Requirements

- ER-01：MUST 在相同 OCR、split、schema 與硬體條件比較 B0/B1/B2。
- ER-02：MUST 報 OCR CER/WER、欄位 F1/Exact Match、異常 macro-F1/PR-AUC、false auto-accept、evidence coverage、latency/RAM。
- ER-03：MUST 提供 per-class results、混淆矩陣、95% CI 與 error analysis；不得只報 accuracy。
- ER-04：MUST 做至少一項 held-out template 測試與一項 image degradation 測試。
- ER-05：SHOULD 做移除 inventory/rules/evidence gate 的 ablation。
- ER-06：MUST 記錄 OS、CPU、RAM、Python、套件、model/prompt/rule 版本與 seed。
- ER-07：MUST 在測試前凍結 primary metric、threshold 與 exclusion criteria。

## 6. Non-functional Requirements

| ID | Requirement | Target / verification |
|---|---|---|
| NFR-01 | 可行性 | Python 3.11+；一般 4–8 核 CPU、16 GB RAM 可完成 MVP；實測設備待登錄 |
| NFR-02 | 效能 | **Proposal target：** median ≤30 s/document；同時報 P95 |
| NFR-03 | 可重現 | lock dependencies、fixed seeds、config snapshot、one-command evaluation |
| NFR-04 | 可靠性 | 工具失敗不得產生成功決策；錯誤需帶 trace ID 並可重試 |
| NFR-05 | 安全 | file type/size validation、path isolation、prompt injection 測試、tool allowlist、read-only DB |
| NFR-06 | 隱私 | data minimization、redaction、local-first processing、log retention policy |
| NFR-07 | 可稽核 | append-only log；核心建議 evidence coverage proposal target ≥90% |
| NFR-08 | 可維護 | typed schemas、module boundaries、unit/integration tests、rule versioning |
| NFR-09 | 易用性 | reviewer 在單一畫面看到文件、欄位、異常、證據與核准控制 |
| NFR-10 | 成本 | 開源 local-first；任何付費 API 為可選 adapter 並單獨報成本 |

## 7. 技術選型約束

- Python；資料：pandas、SQLite；UI：Streamlit；API 可選 FastAPI；測試：pytest。
- OCR 候選：PaddleOCR、Tesseract。最終選擇 MUST 由繁中/數字/表格 pilot 決定。
- Agent orchestration 優先採簡單明確的 Python state machine；只有在需求證明必要時才引入重型框架。
- LLM MUST 可替換且非必要依賴；本地小模型或 API 的輸出均需 schema/evidence gate。
- 依賴授權、模型授權與資料授權 MUST 在 README/DESIGN/DATA_CARD 記錄。

## 8. Repository Documentation Requirements

README.md MUST 包含問題、RQ、範圍、架構、安裝、demo、dataset、evaluation、限制、隱私與 citation。DESIGN.md MUST 包含模組 I/O、state machine、資料 schema、規則格式、decision table、evidence/audit model、failure modes、threat model、測試與 ADR。兩者在 MVP 前建立；本 Proposal 階段只定義大綱。

## 9. Out of Scope

- 正式 WMS/ERP 寫入、自動採購、自動財務核銷。
- 無人工監督的高風險決策。
- 大規模模型訓練、GPU 必需的部署、全產業通用規則宣稱。
- 將 SROIE/FUNSD/DocVQA 的結果直接外推成臺灣倉儲實務效能。

## 10. Definition of Done（Proposal）

- RQ1–RQ4、主要指標、baseline 與成功門檻已明定。
- Planner/Tools/Reasoning/Domain Knowledge/Decision 各自有用途、I/O、限制與驗證。
- 架構、流程、行號 pseudocode、dataset 與 experiment matrix 完整。
- 2025–2026 search protocol 與已核對起始來源存在；未核對內容標「待查證」。
- `project_plan.md`、`requirements.md`、`proposal_checklist.md` 交叉一致。


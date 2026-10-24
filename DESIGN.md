# Smart Warehouse AI Agent — Proposed Scheme / Proposed Design

> 版本：v0.1｜日期：2026-10-24  
> 狀態：Target Design + Partial MVP Implementation。第 11 節列出已實作與已測試範圍；其餘均為 Planned。正式 B0/B1/B2 實驗尚未執行，任何效能描述均為 Expected Outcome。

## 1. Design Goal and Scope

本系統把倉儲單據辨識、庫存資料查詢、異常分析、領域規則與人工覆核串成具規劃能力的 Domain AI Agent。原型輸出 recommendation 與 evidence，不直接修改正式 WMS/ERP。主要 scenario 為收貨比對、出貨前檢查、盤點差異及重複單據偵測。

### 1.1 Problem

純 OCR 只能輸出文字，無法自行判斷重複單據、未知 SKU、出庫超量或倉儲政策缺漏；WMS 通常假設輸入已正確結構化。本設計處理從非結構化文件到具證據異常建議之間的安全連接問題。

### 1.2 Requirements

- 接受 JPG、PNG 或 PDF，抽取單號、日期、倉別、品項、數量與棧板型式。
- 查詢 SQLite（Google Sheets 為 Planned），執行重複、欄位、數量與庫存規則。
- Planner 只能選擇 allowlisted tools；高風險、低信心、衝突與錯誤必須 fail-safe。
- 每項 finding 提供 evidence reference；測試資料庫寫入前必須人工確認。
- API key 只由環境變數載入；不得使用真實敏感單據作公開 fixture。

三份可編輯技術表示：

- [System Architecture](architecture.md)：八個編號模組、責任邊界及模組契約。
- [Flowchart](flowchart.md)：完整主流程、Decision、Loop 與 Exception。
- [Algorithm 1](algorithm.md)：輸入、輸出與 92 行 pseudocode。

## 2. Architecture

架構固定為八層：

1. ① User / Application Scenario
2. ② Query / Input
3. ③ Planner & Reasoning Agent
4. ④ Data Acquisition / Retrieval
5. ⑤ Analytics Engine
6. ⑥ Domain Knowledge Integration
7. ⑦ Decision / Recommendation
8. ⑧ Output & Interaction

核心資料流為：

```text
User/Task
  → validated document and trace
  → bounded plan and selected tools
  → OCR/document fields + inventory/history/master data
  → normalized analytics and reconciliation
  → versioned domain rule hits
  → risk/confidence/evidence decision gate
  → recommendation or human review
  → append-only audit output
```

完整 Mermaid 圖見 [architecture.md](architecture.md)。

## 3. Agent Definition and Non-Agent Components

本節同時定義 **Components、AI/Analytics 與 Domain Knowledge** 的責任邊界。③ Planner 是受限 orchestration；OCR、parser、SQL、analytics 與 rules 是可獨立測試的工具，不因被 Agent 呼叫就改稱 AI reasoning。

### 3.1 真正的 Agent 能力

③ Planner & Reasoning Agent 必須至少能：

- 從任務判斷 scenario 與 required fields。
- 依中間結果選擇 OCR、庫存、主檔或歷史查詢工具。
- 發現缺資料後補查、要求補件，或在達到 stop condition 時停止。
- 對 evidence coverage、tool error、source conflict 與 risk 作出不同分支。
- 僅以 schema-constrained JSON 與 evidence IDs 傳遞理由。

若系統永遠依固定順序執行函式，則為 OCR + Rules pipeline（B1），不是 Agent（B2）。

### 3.2 Implementation Boundary

| Component | Implementation type | 說明 |
|---|---|---|
| Task understanding | LLM optional + deterministic intent allowlist | LLM 只映射受控 scenario；不合法意圖拒絕 |
| Plan selection | Finite-state controller；LLM optional | 選擇 allowlisted tool、補查與停止，輸出 validated `PlanStep` |
| OCR | PaddleOCR 或 Tesseract tool | 非 Agent reasoning |
| Image preprocessing | OpenCV/Pillow deterministic functions | rotation、crop、denoise、render PDF |
| Schema parsing | Pydantic + deterministic parser；LLM optional candidate extraction | 最終必須通過 typed schema |
| SQLite/Sheets retrieval | Parameterized read-only adapter | Agent 選擇何時查，SQL/Sheets 函式負責取得資料 |
| Duplicate exact check | Deterministic composite key | confirmed duplicate 的主要依據 |
| Fuzzy duplicate candidate | Statistical/string similarity | 只列候選，不直接定案 |
| Reconciliation | Deterministic Decimal arithmetic | quantity、unit、event/snapshot time |
| Anomaly statistics | pandas/statistical functions | deviation、frequency、optional outlier score |
| Warehouse rules | Versioned deterministic Rule Engine | 規則有 ID、source、severity、tests |
| Evidence reasoning | LLM optional, evidence-constrained | 產生 facts/conflicts/unknowns 摘要，不得創造證據 |
| Decision gate | Deterministic decision table | risk、confidence、coverage、freshness、human requirement |
| Human review | Streamlit form | approve、edit、reject、reprocess |
| Audit | Append-only JSONL | hash、versions、tool calls、decisions、human action |

## 4. Data Flow

### 4.1 Input Data

- 文件：JPG、PNG、PDF。
- 任務：自然語言 query 與 scenario metadata。
- 結構資料：SQLite（預設）或 Google Sheets（選配）。
- 知識：versioned YAML/JSON rules、品項主檔、unit mappings、policy thresholds。

### 4.2 Intermediate Data

- `OCRSpan[]` → `DocumentField[]` → `FactBundle`。
- `InventoryRow[]`, `DocumentHistory[]`, `MasterDataRow[]`。
- `AnalyticFinding[]`, `RuleHit[]`, `EvidenceRef[]`。

### 4.3 Output Data

- Schema-valid result JSON。
- 異常與 recommendation，附 risk、confidence、reason codes、evidence IDs。
- 人工 disposition 與 reprocess request。
- Append-only `AuditEvent` JSONL。

### 4.4 Data Integrity

- 文件以 hash 識別；所有轉換保留 parent evidence reference。
- 數量使用 `Decimal`，日期時間使用 ISO 8601 與明確 timezone。
- 工具 error、empty result、unknown 與 confirmed false 使用不同狀態。
- 人工修改建立新版本，不覆寫原始 OCR、field 或 decision。

## 5. Flow and Exceptions

完整 Mermaid flowchart 見 [flowchart.md](flowchart.md)。主要 exception policy：

- Input invalid：拒絕並要求重新上傳。
- OCR failed：改變前處理後自動重試一次，再失敗轉人工。
- Missing field：關鍵欄位不得以 LLM 猜測，轉人工補件。
- Data unavailable/stale：停止自動判斷，不把 error 當成零庫存。
- Duplicate：exact key 標為 confirmed risk；fuzzy match 只列候選。
- Inventory mismatch：保留多個可能原因，不直接宣稱 root cause。
- Rule conflict：視為 configuration error 或人工審核。
- High risk / low confidence / low coverage：強制 Human Gate。
- Reprocess：沿用 root trace，建立新 attempt，受最大次數限制。

## 6. Algorithm

Algorithm 1 見 [algorithm.md](algorithm.md)，涵蓋：任務理解、bounded planning、工具選擇、OCR 與 retry、欄位 schema、資料擷取、重複檢查、庫存對帳、統計分析、規則推理、信心與 coverage、決策、人工確認與 audit。

關鍵不變量：

1. `NO_WMS_WRITE`：Agent 執行期間不可出現庫存寫入。
2. `NO_UNSUPPORTED_CLAIM`：每個 material claim 必須能解析至 evidence ID。
3. `NO_SILENT_CORRECTION`：任何修正都有 actor、reason、timestamp 與 previous version。
4. `BOUNDED_EXECUTION`：tool allowlist、最大步數、單次自動 OCR retry。
5. `FAIL_SAFE`：未知、矛盾或工具失敗不能轉成 pass。

## 7. Implementation Mapping

以下為 **Target Design / Planned repository mapping**，不是目前已全部存在的檔案；實際 MVP mapping 見第 11 節：

```text
src/smart_warehouse_agent/
├─ app.py                         # Streamlit / API entry
├─ schemas/
│  ├─ task.py                    # TaskEnvelope, UserContext
│  ├─ document.py                # OCRSpan, DocumentField
│  └─ decision.py                # Finding, RuleHit, DecisionRecord
├─ planner/
│  ├─ state_machine.py           # bounded states and transitions
│  ├─ intent.py                  # scenario mapping
│  └─ policy.py                  # tool allowlist and stop conditions
├─ tools/
│  ├─ preprocess.py              # image/PDF preprocessing
│  ├─ ocr.py                     # OCR adapter
│  ├─ sqlite_store.py            # read-only SQLite
│  ├─ sheets_store.py            # optional Google Sheets adapter
│  └─ history.py                 # document history queries
├─ analytics/
│  ├─ normalize.py               # date, Decimal, unit, identifiers
│  ├─ duplicate.py               # exact and fuzzy candidates
│  ├─ reconcile.py               # inventory reconciliation
│  └─ confidence.py              # confidence and coverage
├─ domain/
│  ├─ rule_engine.py             # deterministic evaluation
│  └─ rules/warehouse_v1.yaml    # versioned rules
├─ decision/
│  ├─ risk.py                    # risk assessment
│  └─ gate.py                    # deterministic decision table
└─ audit/
   ├─ evidence.py                # EvidenceRef and integrity
   └─ log.py                     # append-only JSONL
```

| Design module | Planned implementation | Planned verification |
|---|---|---|
| ①–② | `app.py`, `schemas/task.py` | role/scenario/file validation tests |
| ③ | `planner/state_machine.py`, `planner/policy.py` | state transition、loop、unauthorized-tool tests |
| ④ | `tools/*`, `schemas/document.py` | OCR fixtures、read-only DB、Sheets mock tests |
| ⑤ | `analytics/*` | Decimal/unit/time/duplicate/reconciliation tests |
| ⑥ | `domain/rule_engine.py`, rule YAML | per-rule boundary tests、version regression |
| ⑦ | `decision/*` | decision-table coverage、false auto-accept evaluation |
| ⑧ | `app.py`, `audit/*` | UI scenarios、hash、append/replay tests |

## 8. Risk Analysis

| Risk | Cause | Impact | Control | Verification |
|---|---|---|---|---|
| OCR critical-field error | blur、rotation、small font | wrong SKU/quantity | per-field confidence、retry once、human gate | degraded-image suite、CER/field F1 |
| Hallucinated field or rationale | unconstrained LLM | unsupported decision | schema output、evidence IDs、unsupported-claim blocker | adversarial/missing-evidence tests |
| Prompt injection in document | document text contains instructions | unauthorized tool/action | treat document as data、system tool policy、allowlist | injected-document tests |
| Duplicate false positive | fuzzy text similarity | valid receipt blocked | exact vs candidate separation | near-match fixtures、precision |
| Duplicate false negative | OCR error/key variation | double posting risk | composite keys、history query、human review | mutation tests、recall |
| Stale inventory | delayed Sheets/WMS snapshot | false mismatch/pass | mandatory `as_of_time` and freshness gate | stale/missing timestamp tests |
| Unit conversion error | box/piece mapping wrong | large quantity error | versioned unit mapping、Decimal、no implicit conversion | unit boundary tests |
| Rule misconfiguration | missing/conflicting policy | inconsistent decision | versioned rules、conflict check、fail-safe | config validation、regression |
| Data-source outage | network/API/locked DB | missing context | distinguish error from empty result | outage simulation |
| Over-automation | threshold too permissive | dangerous auto-pass | recommendation-only、risk tiers、human gate | false auto-accept and coverage-risk curve |
| Automation bias | reviewer trusts recommendation | human confirms error | show source evidence/uncertainty、require reason on high risk | user study; **待執行** |
| Privacy leakage | document/log contains PII | compliance/reputation | local-first、redaction、retention policy、no sensitive Git data | manual review、PII scan |
| Audit tampering/loss | overwrite or log failure | no traceability | append-only events、hash、fail closed | replay/hash integrity tests |
| Cost/latency | repeated LLM/OCR/API calls | infeasible student deployment | bounded steps、cache、SQLite default、local OCR | median/P95 latency、RAM、call count |

## 9. Security and Privacy Decisions

- Google Sheets 為選配，憑證不得寫入 repository；採最小唯讀 scope。
- SQLite connection 使用 read-only mode，所有查詢 parameterized。
- 上傳文件限制 MIME、size、page count，檔名不直接作 filesystem path。
- 文件中的文字永遠視為 untrusted data，不可改寫 tool policy。
- Audit log 避免保存不必要 PII；retention period 與刪除程序為**待查證的組織政策**。

## 10. Feasibility and Open Decisions

MVP 優先採 Python、PaddleOCR/Tesseract、Pydantic、pandas、SQLite、Streamlit、pytest。Google Sheets 與 LLM API 均為 adapters，不是核心離線流程的必要條件。下列項目尚待 pilot：

- OCR engine 對繁體中文、數字及表格的實測選型。
- LLM 採本地小模型或 API，以及相應成本與資料政策。
- 高風險品項、snapshot 最大年齡、confidence 與 evidence coverage thresholds。
- Google Sheets API quota 與課程 demo 網路可用性。
- 目標電腦 CPU、RAM、median/P95 latency。

上述均標為**待查證**；未完成前不得宣稱架構已達成效能或安全目標。

### 10.1 Data Sources, Tools and Validation

| Area | Current choice | Feasibility / validation |
|---|---|---|
| Documents | 匿名 UTF-8 fixture、JPG/PNG、embedded-text PDF | fixture 已測；真實 image/scanned PDF 待測 |
| Structured data | SQLite | seed、query、unique constraint、audit 已測 |
| UI | Streamlit | import smoke 已執行；瀏覽器人工測試待執行 |
| OCR | pypdf / optional Tesseract | PDF path 已實作未自動測；Tesseract 只測 dependency failure |
| Analytics | Python `Decimal`、pandas dependency | duplicate/SKU/availability 路徑已測；統計模組 Planned |
| Agent | rule-based bounded planner | intent、allowlist、plan length 已有基本實作；dynamic replan Planned |
| Domain knowledge | Python deterministic rules | 部分規則已測；versioned YAML、source mapping Planned |

## 11. MVP Implementation Status（2026-10-24）

設計已轉為第一條可執行流程，實作對應如下：

| Design | Implemented module | Verification status |
|---|---|---|
| ①② UI/Input | `app.py` | Streamlit import/smoke 已執行；瀏覽器人工測試待執行 |
| ③ Planner | `agent/planner.py`, `agent/service.py` | RECEIPT/ISSUE/CHECK 路由、allowlist、bounded plan 已測 |
| ④ OCR/Retrieval | `ocr/`, `database/repository.py` | synthetic OCR 與 SQLite 已測；image OCR 只測 fail-safe；scanned PDF 未實作 |
| ⑤ Analytics | `analytics/checks.py` | duplicate、unknown SKU、出庫可用量已測 |
| ⑥ Domain | `domain/rules.py` | required fields、positive quantity、unit、pallet rules 已測部分路徑 |
| ⑦ Decision | `agent/service.py` | pass、correction、human review、failed 已測 |
| ⑧ Output/Audit | `app.py`, `database/repository.py` | confirmation-before-write、unique constraint、audit events 已測 |

### 11.1 實作與原設計差異

- SQLite 已完成；Google Sheets adapter 尚未實作。
- 使用 bounded rule-based planner；`agent/llm.py` 只提供 `.env` 設定與 fail-explicit boundary，外部 LLM 尚未接入。
- Synthetic UTF-8 provider 用於自動測試。文字型 PDF 使用 pypdf；圖片需外部 Tesseract；掃描型 PDF renderer 尚未實作。
- MVP evidence 能回指來源文字行；word-level OCR bbox 尚未完成。
- JSONL audit 的設計在 MVP 以 SQLite `audit_log` append rows 實作，仍非防竄改 ledger。

### 11.2 實際測試結果

命令：

```powershell
python -m compileall -q agent ocr analytics domain database tests scripts app.py
python -m unittest discover -s tests -v
```

結果：6 tests passed。測試涵蓋成功寫入、確認前不寫入、重複檢查與 DB constraint、缺欄、空白檔案、出庫不足及 OCR dependency failure。這些結果只適用於合成 fixture 與目前程式，不代表真實 OCR 準確度。

## 12. Experimental Design Mapping（尚未執行）

正式比較規格見 [`experiments.md`](experiments.md)。三組方案共用同一組凍結測試資料與 gold labels：

| Baseline | Input-to-decision boundary | Main measured outcomes |
|---|---|---|
| B0 人工輸入與人工核對 | 人員讀取原單據、輸入欄位並依相同政策核對 | 欄位 EM、異常 P/R/F1、重複偵測、時間、人工介入 |
| B1 OCR + Fixed Rules | 固定 OCR、parser、SQLite 查詢與確定性規則；無 planner | OCR/欄位品質、規則異常、時間、人工介入 |
| B2 OCR + Domain AI Agent | 與 B1 共用 OCR/parser/rules，增加有界 planner、工具選擇、證據與升級策略 | B1 指標加 tool selection 與 task completion |

### 12.1 公平比較與資料洩漏控制

- 以供應商／版型群組切分 train/validation/test，規劃比例為 60/20/20；seed 暫定 `20261024`，須於實驗前由指導教師確認並凍結 manifest 與 checksum。
- test set、gold transcription、欄位標註、異常標籤與對應時間點的 inventory snapshot 對三組完全相同。
- B1 與 B2 共用 OCR、parser、資料正規化與 rule version，避免把 OCR 差異誤歸因於 Agent。
- validation set 僅用於凍結 confidence、risk 與升級門檻；test set 不得回饋調參。
- 結果以配對文件為分析單位，規劃報告 bootstrap 95% CI、McNemar test 或 Wilcoxon signed-rank test；實際檢定須依資料分布與樣本量確認。

### 12.2 Implementation-to-metric mapping

| Metric | Implementation evidence | Verification artifact |
|---|---|---|
| OCR 字元準確率 | `ocr/` 原始文字輸出 | gold transcription、CER script（待建立） |
| 重要欄位 Exact Match | parser structured output | normalized gold fields、per-field report（待建立） |
| 異常 Precision/Recall/F1 | `analytics/`、`domain/` findings | adjudicated anomaly labels、confusion matrix（待建立） |
| 重複單據偵測 | SQLite history 與 duplicate check | exact/near-duplicate scenario set（待擴充） |
| 處理時間 | upload-to-result 與 human-confirm timestamps | benchmark log（待建立） |
| 人工介入比例 | decision status / confirmation events | audit query（待建立） |
| 工具選擇／任務完成率 | `agent/planner.py` plan 與 audit | expected-tool labels、completion rubric（待建立） |

### 12.3 Experimental safety boundary

截至 2026-10-24，正式 B0/B1/B2 實驗、真實掃描 OCR benchmark、使用者研究與統計檢定均為 **Not Run**。既有 6 個 automated tests 只證明合成 MVP 路徑與失敗保護可執行，不可作為準確率、效率或優越性結論。所有結果表必須維持空白，直到資料凍結、執行腳本與人工 adjudication 完成。

## 13. How to Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m scripts.init_db
python -m streamlit run app.py
```

完整環境變數、OCR provider 與測試命令見 [README.md](README.md)。Tesseract 為獨立系統依賴；未安裝時圖片 OCR 應明確失敗，不得回傳假結果。

## 14. Results

### 14.1 Observed Engineering Results

- Python source 可編譯。
- 6 個合成資料 automated tests 通過，涵蓋確認前不寫入、確認後寫入、重複阻擋、缺欄、空檔、出庫不足及 OCR dependency failure。
- Streamlit import smoke 通過；瀏覽器互動未人工驗證。

### 14.2 Research Results

**Not Run。** CER、field Exact Match、異常 Precision／Recall／F1、重複偵測準確率、處理時間、人工介入、工具選擇與任務完成率均沒有 observed values。空白結果表見 [experiments.md](experiments.md)。

## 15. Limitations

- Planner 現階段主要是固定七步 bounded orchestration，尚未依中間結果動態選工具。
- Parser 依賴明確欄名與列格式，不能代表任意供應商版型泛化能力。
- 沒有掃描 PDF renderer、Google Sheets、外部 LLM、fuzzy duplicate、snapshot freshness、word-level bbox 或防竄改 audit ledger。
- 規則仍為 Python MVP，尚未完成具 source/version 的 YAML/JSON policy repository。
- 真實圖片 OCR、正式資料集、效能、人因、安全與 B0/B1/B2 實驗皆未完成。

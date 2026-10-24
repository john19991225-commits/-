# Smart Warehouse AI Agent — Proposal 與專案嚴格稽核報告

> 稽核日期：2026-10-24  
> 稽核範圍：目前工作目錄內的 Markdown、Python、測試、設定、合成資料與 SQLite；另以出版社、ACL Anthology、IEEE、NIST、GS1 等原始頁面核對文獻。  
> 證據原則：沒有本機檔案、程式執行結果或外部原始來源支持者，一律列為「未驗證」。本報告不把設計、Expected Outcomes 或單元測試視為正式實驗結果。

## 一、總評與估計分數

本專題的 Proposal 結構完整，研究問題、Deep Research、架構圖、例外流程與實驗 protocol 均高於一般初稿水準；MVP 也確實可執行。然而，最大扣分點是「完整 Agent 設計」與「目前程式實作」之間仍有明顯距離：現有 `RuleBasedPlanner` 對三種 intent 幾乎都產生相同七步流程，外部 LLM adapter、動態補查、freshness、risk × confidence、evidence coverage、重試迴圈與多數 audit invariants 尚未實作。因此，目前較精確的定位是 **可執行的 OCR/Parser + Rules + bounded orchestration MVP**，尚不能以程式證據證明完整 Domain AI Agent 已實現。

| 評分項目 | 權重 | 估計得分 | 判定 |
|---|---:|---:|---|
| Introduction | 20 | 17 | 大致完成，有 baseline 定義衝突 |
| Related Work | 20 | 15 | 結構完整，但有兩項 citation metadata 錯誤及未完成查證 |
| Deep Research | 20 | 15 | 5/3/10 完整，但 claim audit、research log 與引用修正未完成 |
| Proposed AI Agent + System Architecture | 20 | 12 | 設計強，實作只涵蓋子集，Agent 動態性證據不足 |
| Flowchart + Pseudocode + Technical Feasibility | 15 | 10 | 表示完整且 MVP 可跑，但 pseudocode 大幅超前實作，Mermaid 未 renderer 驗證 |
| GitHub + DESIGN.md + 完整度 | 5 | 3 | 文件、source、tests 齊備，但目前不是 Git repository，缺 LICENSE/lock/CI |
| **總分** | **100** | **72** | **可作 Proposal 草稿；不宜宣稱完整 Agent 或實驗完成** |

分數是依現有證據的保守估計，不代表授課教師正式成績。

---

## 二、Introduction — 17/20

### 1. 老師要求

問題重要性有可靠數據支持；說明背景、真實問題、現有限制、創新性、Research Questions、可測量目標及預期貢獻；不得把 Expected Outcomes 寫成完成結果。

### 2. 對應檔案與章節

- `proposal.md`：Abstract A–F（第 12–36 行）、Introduction 2.1–2.6（第 40–102 行）。
- `requirements.md`：Scope、Functional Requirements、Evaluation Requirements。
- `experiments.md`：Research Questions、Baselines、Metrics。

### 3. 實際證據

- `proposal.md:16`、`:44` 引用 2025 Warehouse/DC survey，並明確限制其外推性。
- `proposal.md:58–60` 定義重複單據、SKU 混淆、負庫存、表頭明細不一致、批號／效期缺漏及資料衝突。
- `proposal.md:68–76` 提出五項設計創新且未宣稱全球首創。
- `proposal.md:78–93` 有 RQ1–RQ4 與五項 objectives。
- `proposal.md:97–102` 有四項 Expected Contributions。
- `proposal.md:7`、`:34–36` 清楚標示未執行實驗與 Expected Outcomes。

### 4. 完成狀態

**大致完成。** 問題—限制—創新—RQ—貢獻鏈條可追蹤，研究語氣大致保守。

### 5. 缺漏與修正建議

1. `proposal.md:32` 把 B0/B1/B2 寫成「純 OCR／OCR + Rules／OCR + Agent」，但 `experiments.md:19–39` 與本次課程要求定義為「人工／OCR + Rules／OCR + Agent」。這會破壞 RQ、baseline 與簡報的一致性，必須全域統一。
2. `proposal.md:80` 的 RQ1 仍問「比純 OCR」，無法直接回答人工 baseline 的效率與正確度比較。建議拆成欄位品質比較與整體 workflow 比較。
3. 目前 objectives 中的資料集、append-only trail 與公平比較仍是規劃，不宜在口頭報告說成完成。

### 6. 估計得分及依據

**17/20。** 結構、問題明確性與可測量性佳；因 baseline 定義衝突以及部分目標尚無執行證據扣 3 分。

---

## 三、Related Work — 15/20

### 1. 老師要求

至少一半 AI Technology、一半 Warehouse Domain Knowledge；優先使用 2025–2026 正式文獻；有 Article Summary Table；說明 findings、limitations 與 research gap；所有 DOI、作者、數據可追溯。

### 2. 對應檔案與章節

- `proposal.md` 3.1–3.5（第 106–181 行）。
- `proposal.md` Article Summary Table（第 148–163 行）。
- `proposal.md` References（第 225–251 行）與待查證清單（第 255–262 行）。

### 3. 實際證據

- `proposal.md:110` 明定 5 篇 AI 與 5 篇 Warehouse research，比例各半；GS1、產業調查與 NIST 另列。
- `proposal.md:118–146` 對 OCR/KIE、document agent、IoT、Digital Twin、inventory anomaly、order picking 與 GS1 分類討論。
- `proposal.md:150–162` 表格包含 Ref.、Year、Problem、AI Method、Domain Knowledge、Dataset、Findings、Limitation。
- `proposal.md:165–181` 使用 Existing Research → Limitations → Research Gap → Our Project。

### 4. 完成狀態

**部分完成。** 章節設計與文獻比例符合要求，但 citation ledger 尚未完全可靠。

### 5. 文獻與數據逐筆查核

| Ref. | 查核結果 | 判定與問題 |
|---|---|---|
| [1]/DR1 DocAgent | ACL Anthology 的作者、EMNLP 2025、頁碼與 DOI `10.18653/v1/2025.emnlp-main.893` 相符 | 已驗證 |
| [2]/DR2 AID-Agent | 題名、作者、REALM 2025、80–88 相符；但 ACL 頁面**有** DOI `10.18653/v1/2025.realm-1.6` | 文獻存在；Proposal「ACL 未列 DOI」錯誤，須修正 |
| [3]/DR3 Principe et al. | ACL Anthology metadata 與 243–254 相符，頁面沒有 DOI | 已驗證 |
| [4]/DR4 SROIE | DOI `10.1109/ICDAR.2019.00244`、作者與頁碼相符 | 已驗證 |
| [5]/DR5 DocVQA | DOI `10.1109/WACV48630.2021.00225`、12,000+ images、50,000 questions 相符 | 已驗證 |
| [6]/DR6 IoT warehouse review | ScienceDirect 題名、Procedia CS 253、1236–1245、DOI `10.1016/j.procs.2025.01.185` 相符 | 已驗證 |
| [7]/DR7 inventory anomaly | IEEE 頁面確認題名、會議、DOI、12,358 SKUs 與摘要所稱 F1 87.3% | 數據為「摘要報告」可引用；作者及全文仍未驗證，現有標示適當 |
| [8]/DR8 AI order picking | 題名、四位作者、期刊、頁碼與 DOI `10.1007/s11846-025-00858-1` 相符 | 已驗證 |
| [9]/DR9 smart warehousing | ScienceDirect 確認 2026、vol. 19、100340、DOI `10.1016/j.clscn.2026.100340` | 已驗證 |
| [10]/DR10 GS1 | 官方頁確認 Release 1.3、Ratified、July 2019 | 已驗證 |
| [11]/DR11 survey | 原始文章確認 n=101、WMS 87%、manual collection 51%、inventory accuracy 76%、SKU 7,790→9,565 | 已驗證；屬產業調查，不是 peer-reviewed evidence |
| [12]/DR12 NIST AI RMF | NIST 官方頁與 DOI `10.6028/NIST.AI.100-1` 相符 | 已驗證 |
| [13] Digital Twin review | ScienceDirect 確認 2026、ICT Express 12(2)、459–479、DOI `10.1016/j.icte.2026.01.009` | 已驗證 |
| DR13 NIST AI 600-1 | NIST 官方頁確認 2024 publication 與 DOI `10.6028/NIST.AI.600-1` | 已驗證；References 應補完整作者或採機構作者格式 |
| DR14 DeHoratius & Raman | INFORMS 確認 DOI、作者、54(4):627–641；摘要有 370,000 records、37 stores、65% inaccurate | 已驗證 |
| DR15 Hardgrave et al. | DOI `10.1111/poms.12010`、作者、22(4):843–856 相符 | 已驗證 |
| DR16 Destro et al. | DOI `10.1590/0103-6513.20220077` 與四位作者相符 | 已驗證 |
| DR17 Rao et al. | Wiley 確認 DOI `10.1111/jbl.12232`；完整作者為 S. Rao, S. C. Ellis, T. J. Goldsby, D. Raju | 已驗證；應補完整作者 |
| DR18 Bertolini et al. | DOI `10.3233/RFT-150069`、作者及題名相符 | 已驗證 |
| DR19 Barratt et al. | Wiley 確認作者為 Mark Barratt, Thomas J. Kull, Anníbal Camara Sodero，DOI 與頁碼相符 | 已驗證；目前 initials 過度簡化但非虛構 |
| DR20 | DOI `10.1016/j.jom.2015.07.006` 與題名存在，但正確作者是 **Howard Hao-Chun Chuang、Rogelio Oliva** | **引用作者錯置**；目前的 M. A. Waller et al. 必須移除 |

查核結論：未發現明確「虛構 DOI」，但發現一筆 DOI 遺漏誤述（AID-Agent）及一筆 DOI—作者錯置（DR20）。在修正前，不可宣稱所有 References 已完成逐筆驗證。

主要查核來源：[ACL DocAgent](https://aclanthology.org/2025.emnlp-main.893/)、[ACL AID-Agent](https://aclanthology.org/2025.realm-1.6/)、[IEEE inventory anomaly](https://ieeexplore.ieee.org/abstract/document/11139221/)、[ScienceDirect IoT review](https://www.sciencedirect.com/science/article/pii/S1877050925001930)、[GS1 guideline](https://ref.gs1.org/guidelines/logistic-label/1.3.0/)、[2025 Warehouse/DC survey](https://www.scmr.com/article/2025-warehouse-dc-operations-survey-tech-adoption-marches-on)、[NIST AI RMF](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10)、[Wiley DR20](https://onlinelibrary.wiley.com/doi/10.1016/j.jom.2015.07.006)。

### 6. 估計得分及依據

**15/20。** 文獻分類、比例、summary table 與 gap 論證完整；因 DR20 作者錯置、AID-Agent DOI 誤述、[7] 作者未核對、未保存完整 search log，以及部分「已檢視全文」無本機閱讀紀錄可重播而扣 5 分。

---

## 四、Deep Research — 15/20

### 1. 老師要求

五個核心思維模式各含定義、案例、證據、設計影響；三項真實專業爭論呈現雙方 evidence、consensus 與 unresolved issues；十題涵蓋多種推理型態並轉成 Domain Rules、Agent Planning 與異常邏輯。

### 2. 對應檔案與章節

- `deep_research.md` Q1（第 19–133 行）。
- `deep_research.md` Q2（第 138–213 行）。
- `deep_research.md` Q3（第 217–297 行）。
- `deep_research.md` 4.1–4.4（第 301–363 行）。
- `proposal.md` 第四部分（第 185–221 行）。

### 3. 實際證據

- 五個 mindsets 皆有固定四段結構，主題涵蓋流程守恆、追溯、fitness for use、風險分級與閉環校正。
- 三項 controversies 分別是 automation vs. HITL、rules vs. learning/LLM、RFID visibility vs. reconciliation；每項分開列 Evidence、Current Consensus、Unresolved Problems。
- U1–U10 明確標記 Why、What-if、Trade-off、Failure、Evidence、Comparison、Design Decision、Real-world Scenario。
- `deep_research.md:303–355` 已轉為 rule table、planner state/action 與 risk design 草案。

### 4. 完成狀態

**部分完成。** 內容框架完成，但證據工程尚未達可重現 systematic review 標準。

### 5. 缺漏與修正建議

1. 修正 DR20 作者；補齊 DR17 與 DR19 metadata。
2. 新增 `research_log.md`，記錄資料庫、完整 query、查詢日期、result count、去重與排除原因。目前只描述方法，沒有可重播紀錄。
3. 為五個 mindset 與三個 controversy 建立 claim-to-source matrix；目前多個結論以一組引用共同支持，難以逐句稽核。
4. `deep_research.md:75` 的「99% 但 10→100」是清楚的假設案例，不是研究結果；建議明標「illustrative hypothetical example」，避免被誤讀為觀測數據。
5. Domain rules 尚未形成實際 versioned YAML/JSON 與 source field；目前只存在 Python 常數與規則函式。

### 6. 估計得分及依據

**15/20。** 5/3/10 與設計轉換完整，分析深度良好；引用錯誤、缺 search log、缺 claim-level evidence ledger、領域規則尚未資料化而扣 5 分。

---

## 五、Proposed AI Agent + System Architecture — 12/20

### 1. 老師要求

Agent 必須有真正的任務理解、規劃、工具選擇、領域知識與有限決策；架構需區分 LLM、確定性規則與統計模組，涵蓋 OCR、前處理、SQLite/Sheets、重複檢查、人工確認與 audit。

### 2. 對應檔案與章節

- `architecture.md` 架構圖、責任邊界與八模組契約。
- `DESIGN.md` 2–9、11–12。
- `agent/planner.py`、`agent/service.py`、`ocr/`、`analytics/checks.py`、`domain/rules.py`、`database/repository.py`、`app.py`。

### 3. 實際證據

- 架構設計包含 ①–⑧、OCR、preprocess、SQLite/Sheets、history、duplicate、reconciliation、rules、Human Gate 與 log。
- `architecture.md` 的責任表明確區分 LLM/Agent、deterministic rules、statistics 與 human。
- `agent/planner.py:14–22` 有 allowlist；`:24–30` 有 intent mapping；`:48–49` 有最多八步的安全檢查。
- `agent/service.py` 實際串接 OCR、parser、history、inventory、analytics、rules、decision status 與 audit。
- `app.py:61–66` 要求 checkbox 與 actor 後才寫入測試資料庫。
- `database/repository.py:49–67` 有 documents 與 audit_log；`:99–104` 有 history query；`:129–130` 阻擋 duplicate write。

### 4. 完成狀態

**設計完成、實作部分完成。** Architecture 與 DESIGN 彼此一致，但都描述 target architecture；實際 MVP 只覆蓋其中一部分。

### 5. 關鍵差距與修正建議

| 設計宣稱 | 實際程式證據 | 判定 |
|---|---|---|
| Planner 依中間結果動態選工具／補查 | `build_plan()` 對 RECEIPT/ISSUE/CHECK 都建立相同七步；service 也固定依序呼叫 | **未實作**；目前較像固定 orchestration |
| LLM schema-constrained planning/reasoning | `agent/llm.py` 只有設定邊界，provider 啟用即 `NotImplementedError` | **未實作** |
| OCR preprocessing + retry | `ocr/providers.py` 沒有 rotate/crop/denoise/retry | **未實作** |
| OCR bbox 與真實 confidence | `_line_evidence()` 的 bbox 為 `None`，confidence 是 provider 固定 0.80/0.95/1.0 | **未實作／非校準信心** |
| Google Sheets | 無 adapter | **未實作** |
| fuzzy duplicate、statistics、freshness | analytics 只有 exact document number、SKU existence、issue availability | **未實作** |
| versioned rules with ID/source/severity | `domain/rules.py` 為硬編碼 Finding，沒有 rule version/source | **部分實作** |
| risk × confidence × coverage decision | service 使用 `bool(findings) or confidence < 0.75` | **簡化實作** |
| append-only JSONL / immutable audit | SQLite 普通 table，可更新或刪除，無 hash chain | **部分實作，非防竄改** |
| human approve/edit/reject/reprocess | UI 只有 confirm/write；沒有 edit/reject/reprocess workflow | **部分實作** |
| read-only production inventory | repository connection 可寫；但目前只操作測試 DB，正式 WMS 未連接 | **MVP 範圍內可接受，需清楚標示** |

另有一個程式瑕疵：`OptionalLLMService.available()` 在 provider 為 `disabled` 時回傳 `True`，語意疑似顛倒，且沒有測試覆蓋。

`DESIGN.md:4` 仍寫「尚未實作與驗證」，但第 11 節又記錄 MVP 已實作。應把首頁狀態改為「Target Design + Partial MVP Implementation」，避免自相矛盾。

### 6. 估計得分及依據

**12/20。** Target architecture 的責任邊界與 failure handling 很好；但若評分包含 GitHub 實作，Planner 的動態規劃證據不足，主要決策仍是固定 pipeline 與簡單閾值，因此扣 8 分。

---

## 六、Flowchart + Pseudocode + Technical Feasibility — 10/15

### 1. 老師要求

流程圖需含主流程、decision、loop、exception；Pseudocode 需有 Input、Output、逐行編號並對應實作；技術應可在一般學生電腦執行且有測試證據。

### 2. 對應檔案與章節

- `flowchart.md` Mermaid 與決策／例外說明。
- `algorithm.md` Input、Output、01–92 行演算法、責任與複雜度。
- `experiments.md` Dataset、三 baseline、metrics、protocol 與空白結果表。
- `requirements.txt`、`tests/test_mvp.py`、`README.md` Run/Test。

### 3. 實際證據

- Flowchart 含 file validation、OCR retry、missing fields、data source failure、duplicate、inventory mismatch、rule conflict、Human action 與 reprocess loop。
- Pseudocode 有明確 I/O、92 行行號、tool errors、stale snapshot、unsupported claim、risk gate、human loop 及 no-write assertion。
- 技術選型為 Python 3.11、Streamlit、SQLite、pandas、Pillow、pypdf、pytesseract，符合學生電腦可行方向。
- `experiments.md` 的正式結果維持 Not Run，沒有假數據。

### 4. Mermaid 與 DESIGN 一致性

| 檢查 | 結果 |
|---|---|
| Architecture ①–⑧ 編號與 DESIGN 2 | 一致 |
| Planner→OCR/Inventory/History、Analytics→Rules→Decision→Output | 與 DESIGN 主要資料流一致 |
| Human reprocess 回 Planner | architecture、flowchart、DESIGN 一致 |
| OCR retry、missing field、duplicate、inventory mismatch、source stale | flowchart 與 DESIGN 第 5 節一致 |
| Audit | architecture 表示 JSONL，MVP 實際是 SQLite rows；DESIGN 第 11 節有揭露差異 |
| Mermaid renderer 驗證 | **未驗證**；本機沒有 `mmdc`。就文字結構人工檢視未見明顯語法錯誤，但不可聲稱已成功 render |

### 5. Pseudocode 與程式映射

| Algorithm lines | 實作模組 | 狀態 |
|---|---|---|
| 03 hash/trace | `agent/service.py` | 已實作 |
| 04/09 understand/build plan | `agent/planner.py` | 簡化實作；非動態 plan |
| 14–22 preprocess/retry | 無對應 | 未實作 |
| 24–30 parse/normalize/validate | `ocr/parser.py`、`domain/rules.py` | 部分實作 |
| 33–35 inventory/history/master | `database/repository.py` | inventory/history 已實作；master data 未獨立實作 |
| 39–40 snapshot freshness | 無 `as_of_time` 欄位 | 未實作 |
| 43 exact duplicate | `find_document()` + `analytics/checks.py` | 已實作，但只用 document_no |
| 44 fuzzy candidate | 無對應 | 未實作 |
| 45 reconciliation | `analytics/checks.py` | 僅 ISSUE availability，部分實作 |
| 46 statistics | 無對應 | 未實作 |
| 50 versioned rules | `domain/rules.py` | 規則有 severity，但無 ID/version/source |
| 57–65 evidence reasoning/coverage/risk | `service.py` 最低 confidence + findings | 大幅簡化 |
| 67–77 decision | `service.py` | 部分實作 |
| 79 no inventory write | analyze 不寫；確認後寫測試 documents table | 核心分析路徑符合，但沒有 assertion |
| 82–90 review/reprocess | `app.py` | 只有 confirm/write，未實作 edit/reject/reprocess |
| 91 audit | `repository.append_audit()` | 已實作 SQLite event；非 hash-chained append-only |

### 6. 實際自動化測試紀錄

執行環境與命令：

```text
Python 3.11.9
python -m compileall -q agent ocr analytics domain database tests scripts app.py
python -m unittest discover -s tests -v
python -m pip check
python -c "import app; print('streamlit import: PASS')"
```

實際結果：

```text
compileall: PASS
Ran 6 tests in 0.117s
OK
No broken requirements found.
streamlit import: PASS
```

六項測試均通過：confirmation-before-write、duplicate detection/write block、missing fields、empty file、image OCR fail-safe、insufficient stock。Streamlit bare import 產生預期的 `missing ScriptRunContext` warnings；這不等於瀏覽器端 UI 已人工驗證。

未驗證項目：真實圖片 OCR、embedded-text PDF automated test、掃描 PDF、OCR retry、效能、RAM、CER/field EM/F1、三 baseline、使用者研究及 Mermaid render。

### 7. 估計得分及依據

**10/15。** 文件表示完整、實驗未造假、MVP 測試通過；但 pseudocode 多數進階步驟未映射至程式、Mermaid 未 render、真實 OCR 與正式 feasibility benchmark 未執行，扣 5 分。

---

## 七、GitHub + DESIGN.md + 完整度 — 3/5

### 1. 老師要求

Repository 應有 README、DESIGN、source code、依賴、設定範例、匿名 sample、測試與可重現指令；不得包含 key 或敏感資料；應能用 Git history 稽核。

### 2. 對應檔案

- `README.md`、`DESIGN.md`、`.env.example`、`.gitignore`、`requirements.txt`。
- `app.py`、`agent/`、`ocr/`、`analytics/`、`domain/`、`database/`、`scripts/`、`tests/`、`data/`。

### 3. 實際證據

- README 有 project flow、structure、requirements、configuration、run、test、supported fields、known limitations。
- DESIGN 有 architecture、data flow、algorithm mapping、risk analysis、security、MVP status 與 experimental mapping。
- `.env.example` 不含真實 key；`.gitignore` 排除 `.env`、DB、uploads 與 private results。
- `data/synthetic_receipt.txt`、SQLite seed 與測試資料均為匿名／合成資料。
- Source code 與 6 個 tests 實際存在且測試通過。

### 4. 完成狀態

**部分完成。** 本機專案結構完整，但不是可稽核的 GitHub repository。

### 5. 缺漏與修正建議

1. `git rev-parse --is-inside-work-tree` 實際回傳 fatal：目前目錄**不是 Git repository**；無法檢查 history、branch、commit 或 remote，也不能確認 GitHub 已上傳。
2. 缺 LICENSE、dependency lock/hash、CI workflow、CONTRIBUTING、data/model license inventory。
3. `data/warehouse.db` 實際存在工作目錄；雖 `.gitignore` 已排除，但因沒有 Git history，無法證明從未提交。
4. requirements 使用 version ranges，不足以完全重現環境。
5. README 應增加 OS/Tesseract 安裝方式、真實 OCR smoke test 與 limitations 對照表。

### 6. 估計得分及依據

**3/5。** 必要文件、source、測試與安全設定齊備；因不是 Git repository、缺授權與鎖版、無 CI/history 證據扣 2 分。

---

## 八、優先修正清單

### P0 — 提交前必修

1. **修正文獻錯誤：** DR20 作者改為 Howard Hao-Chun Chuang 與 Rogelio Oliva；AID-Agent 補 DOI `10.18653/v1/2025.realm-1.6`，同步更新 `proposal.md`、`deep_research.md` 與 slides。
2. **統一 baseline：** 全專案固定 B0 人工輸入與人工核對、B1 OCR + Fixed Rules、B2 OCR + Domain AI Agent；修正 `proposal.md:32`、RQ1、summary table、slides 與 checklist。
3. **誠實重新命名實作狀態：** 明列 target architecture 與 implemented MVP；不得把目前固定七步 `RuleBasedPlanner` 宣稱為已完成的動態 Agent。
4. **修正 DESIGN 首頁矛盾：** 由「尚未實作」改成「部分 MVP 已實作；完整架構未完成」。
5. **建立 Git repository 前做秘密與資料掃描：** 加 LICENSE，確認 `data/warehouse.db`、`.env`、上傳文件不進 history。

### P1 — 顯著提高分數

6. 讓 Planner 至少依 intent、missing fields、tool error 與中間結果產生不同 plan，並新增 unauthorized tool、max step、dynamic branch tests。
7. 實作並測試 image OCR、embedded PDF fixture、scanned PDF rendering 與一次 preprocessing retry；保存 bbox/word confidence。
8. 將 Domain Rules 移至 versioned YAML/JSON，加入 `rule_id`、`source`、`version`、`severity`、適用 scenario 與 boundary tests。
9. 實作 inventory `as_of_time`、freshness gate、evidence coverage、risk table、human edit/reject/reprocess；補 prompt-injection 與 audit-integrity tests。
10. 建立 `research_log.md` 與 claim-to-source ledger，逐項關閉所有「待查證」。
11. 安裝 Mermaid CLI 或使用可信 renderer，將兩張圖實際 render 並保存檢查結果。

### P2 — 正式實驗前完成

12. 凍結資料 manifest、license、split、seed、primary endpoint、exclusion criteria 與 gold-label adjudication。
13. 建立 CER、field EM、anomaly F1、duplicate、time、human intervention、tool selection 與 task completion 的 evaluation scripts。
14. 在同一 test set 執行 B0/B1/B2；結果只填 observed values、sample size、CI、失敗案例與硬體資訊。
15. 加入 reproducible lock file、CI、CONTRIBUTING、data card、model card 與 release tag。

## 九、最終判定

目前專案具備一份內容扎實的 Proposal、完整的 target design、可執行的合成資料 MVP 與基本測試，但尚未具備下列三種證據：完整 Domain AI Agent 行為、真實 OCR／正式比較實驗、可稽核 GitHub history。因此最安全的提交敘述是：

> 「已完成 Proposal、Experimental Protocol 與 rule-based bounded orchestration MVP；完整 Agent、真實 OCR benchmark 與三 baseline 實驗尚待實作／執行。」

若修正 P0 並完成 P1 的核心 Agent 分支與真實 OCR 測試，預估可顯著改善 Related Work、Agent Architecture、Technical Feasibility 與 GitHub 四個區塊的得分。

# Proposal 評分檢核表

> 專題：Smart Warehouse AI Agent  
> 使用方式：`[ ]` 未完成、`[~]` 進行中、`[x]` 已有可驗證證據。Proposal v0.1 的規劃存在不等於實驗完成。

## 一、Introduction — 20%

- [x] 以實際倉儲單據、庫存差異與人工覆核說明問題。
- [x] 清楚區分 OCR、資訊抽取、異常分析與 Agent 決策。
- [x] 定義 RQ1–RQ4，且每題可由指標回答。
- [x] 定義使用者、使用情境、輸入、輸出、範圍及 out-of-scope。
- [x] 列出可測量 proposal targets，沒有冒充已完成結果。
- [x] 正式 Proposal 以可信資料支持問題規模；若找不到則標「待查證」。
- [x] 將貢獻濃縮為 3–4 點，且未宣稱未經系統性檢索的「首創」。

**得分 Gate：** 問題 → 研究缺口 → RQ → 貢獻能形成一條可追蹤論證鏈。

## 二、Related Work — 20%

- [x] 規劃 OCR/KIE、document understanding、agentic document AI、inventory anomaly、human oversight 五類。
- [x] 起始來源包含可追溯的 ACL、IEEE、NIST、GS1 與資料集官方頁面。
- [x] 方案比較涵蓋純 OCR、OCR + Rules、OCR + Agent。
- [x] 已建立 Article Summary Table：任務、方法、domain knowledge、dataset、findings、限制。
- [~] DOI、作者、venue、年份與頁碼已多數由原始來源整理；標示「待查證」者仍須逐筆人工複核。
- [x] 將 peer-reviewed、preprint、標準與產業／官方資料清楚標示來源類型。
- [x] 不以未核對的效能數字當作本專題成果；無法查證者寫「待查證」。
- [x] 以 Existing Research → Limitations → Research Gap → Our Project 說明差異。

**得分 Gate：** 每個關鍵技術選擇至少有來源或被清楚標記為設計假設。

## 三、Deep Research — 20%

- [x] 定義 2025–2026 時間窗、資料庫、搜尋詞、納入／排除條件。
- [x] 經典 benchmark 與現行官方規範可作時間窗外背景資料。
- [x] 2026 competition／未正式發表結果標明狀態，不當成已證實結論。
- [ ] 保存完整 query、日期、結果數、去重與排除原因於 `docs/research_log.md`。
- [~] 核心主張已引用多類原始／官方來源；仍須完成逐項雙來源 claim audit。
- [~] 已引用 GS1 並區分確定性規則與本地政策；完整欄位對照表仍待補。
- [x] 已討論資料授權、隱私、偏差與 domain shift 風險。
- [x] 已納入 hallucination、prompt injection、tool misuse、automation bias 風險與控制。
- [~] 已標示檢索時間與 2025–2026 範圍；提交前更新流程仍須人工執行。

**得分 Gate：** 查詢可重現、來源可點回、主張與證據一一對應，且誠實呈現研究缺口。

## 四、Proposed AI Agent — 20%

- [x] Planner 定義 state、allowed tools、step limit 與 stop conditions。
- [x] 每個 Tool 均有用途、輸入、輸出與驗證方法。
- [x] Reasoning 採 evidence-first，不保存或要求隱藏思考過程。
- [x] Domain Knowledge 使用可版本化規則與來源欄位。
- [x] Decision 使用 risk × confidence，並有 human gate。
- [x] 明定 recommendation-only，不直接寫回正式庫存。
- [x] 有 evidence pointer、trace ID、input hash 與 append-only audit log 設計。
- [ ] 完成 decision table 的數值門檻；以 validation set 調整並在 test 前凍結。
- [~] DESIGN 已有 threat model；prompt-injection automated test 尚未建立。
- [x] 已以匿名合成入庫案例實作 planner → tools → rules → decision → review。

**得分 Gate：** 系統行為確實是能規劃、用工具、用 domain knowledge、作有限決策與升級的 Agent，而非 OCR 後接聊天介面。

## 五、Flowchart / Pseudocode / Feasibility — 15%

- [x] 有端到端 Mermaid 架構圖與人工覆核分支。
- [x] 有逐行編號、具停止條件與安全斷言的 pseudocode。
- [x] Dataset 分公開 pretest、自製主資料、配對庫存情境。
- [x] 指標涵蓋 OCR、KIE、異常、決策安全、稽核、延遲與資源。
- [x] `experiments.md` 已定義三 baseline、公平控制、影像條件與 held-out template 比較。
- [x] 技術選型以 Python、SQLite、pandas、開源 OCR、Streamlit 為主。
- [ ] 以真實目標電腦記錄 CPU/RAM/OS 並完成 30–50 張 pilot benchmark。
- [~] 已規劃 group split、seed、primary metric 與 exclusion criteria；尚未經教師確認及凍結 manifest。
- [ ] 實驗執行後只在 Observed Results 填實測值、CI 與 error analysis。
- [ ] 若未執行，所有敘述維持 `Expected Outcomes`。

**得分 Gate：** 一般學生電腦能做出 MVP；任一結果都能由固定資料、設定與程式重現。

## 六、GitHub / DESIGN.md — 5%

- [x] 已規劃 repository tree。
- [x] 已定義 README.md 必備章節。
- [x] 已定義 DESIGN.md 必備章節。
- [x] 已建立 `project_plan.md`、`requirements.md`、`proposal_checklist.md`。
- [x] 已建立實際專案 folders、README.md、DESIGN.md 與可執行 MVP。
- [~] 已加入 `.gitignore`；LICENSE、environment lock 與完整資料／模型授權清單仍待補。
- [x] 已加入匿名合成 sample、測試方式與重現指令；contribution 規則待 GitHub 階段補充。
- [ ] 確認 Git history 不含個資、金鑰或未授權文件。

**得分 Gate：** 新使用者依 README 能理解、安裝與重現；DESIGN 能解釋重要決策與限制。

## 七、總分與阻擋條件

| 區塊 | 權重 | 自評（完成正式 Proposal 時填） | Evidence link |
|---|---:|---:|---|
| Introduction | 20 | — | `proposal.md` |
| Related Work | 20 | — | `proposal.md` |
| Deep Research | 20 | — | `deep_research.md`；完整 research log 尚待建立 |
| Proposed AI Agent | 20 | — | `DESIGN.md` |
| Flowchart/Pseudocode/Feasibility | 15 | — | `architecture.md`, `flowchart.md`, `algorithm.md`, `experiments.md` |
| GitHub/DESIGN.md | 5 | — | `README.md`, `DESIGN.md` |
| **Total** | **100** | **—** | |

下列任一情況視為提交阻擋：

- [ ] 有杜撰或無法回溯的 DOI、作者、數據或研究結果。
- [ ] 未執行的實驗以完成式或 Observed Results 呈現。
- [ ] 高風險／低信心案件可跳過人工覆核。
- [ ] 核心模組缺用途、輸入、輸出或驗證方式。
- [ ] baseline 使用不同資料切分或不公平的前處理。
- [ ] GitHub 含個資、API key、商業機密或未授權資料。

## 八、提交前逐項簽核

- [ ] 研究負責人：RQ、metrics、Expected/Observed 標示正確。
- [ ] 文獻負責人：metadata、DOI、publication status 與引用逐筆核對。
- [ ] 資料負責人：license、consent、de-identification、split leakage 已檢查。
- [ ] 工程負責人：版本、測試、資源需求、failure handling 可重現。
- [ ] 指導教師／domain reviewer：規則來源、severity、人工權限與限制合理。

## 九、本次 Quality Check（2026-10-24）

| 狀態 | 項目 | 證據／下一步 |
|---|---|---|
| 已完成 | Proposal 第一至三部分與集中 References | `proposal.md` |
| 已完成 | 5 Mindsets、3 Controversies、10 Questions | `deep_research.md` |
| 已完成 | Agent architecture、flowchart、逐行 pseudocode | `architecture.md`、`flowchart.md`、`algorithm.md` |
| 已完成 | 三 baseline、指標公式、公平比較與空白結果表 | `experiments.md`；狀態為 Not Run |
| 已完成 | 18 頁投影片內容、建議圖表與逐頁講稿 | `proposal_slides.md` |
| 已完成 | 匿名合成 MVP 路徑與 6 個 automated tests | `README.md` 測試紀錄；不代表正式實驗結果 |
| 部分完成 | 文獻 metadata 與 claim-level evidence audit | 逐筆處理所有「待查證」，補 `research_log.md` |
| 部分完成 | 圖片／PDF OCR | embedded-text PDF 已實作；掃描 PDF 與本機 Tesseract 實測待完成 |
| 部分完成 | Dataset、授權與 split | 設計已定義；資料蒐集、授權、去識別、manifest/checksum 未凍結 |
| 部分完成 | Security evaluation | 風險已設計；prompt injection、tool misuse 測試案例待建立 |
| 未完成 | 正式 B0/B1/B2 實驗與統計比較 | 結果表保持空白，不得填 Expected 值 |
| 未完成 | 30–50 張 pilot 與真實目標電腦 benchmark | 記錄 CPU/RAM/OS、median/P95、錯誤案例 |
| 未完成 | PPTX 匯出與人工版面檢查 | 以 `proposal_slides.md` 轉換後檢查字型、圖表與引用 |
| 未完成 | Git repository、CI、LICENSE 與 immutable history audit | 目前目錄非 Git repository |
| 需人工確認 | primary endpoint、樣本數、60/20/20 split、seed、排除條件 | 指導教師核准後才可 preregister/freeze |
| 需人工確認 | 高風險規則、庫存 freshness 與 confidence 門檻 | 倉儲 domain reviewer 簽核 |
| 需人工確認 | 人工 baseline 操作者、同意程序及隱私政策 | 研究倫理／課程要求確認 |
| 需人工確認 | 最終簡報取捨、學校模板與報告時間 | 依教師格式調整 18 頁內容 |

### 提交判定

目前可提交作為 **Proposal 與 Experimental Protocol 草稿**，不可標示為完成實驗的 Final Results。正式送出前至少必須完成文獻待查證清理、教師／domain reviewer 簽核、資料與評估 protocol 凍結，以及 PPTX 人工檢查。

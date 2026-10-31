# Smart Warehouse AI Agent — Proposal Presentation

> 建議頁數：18 頁｜建議時間：15–18 分鐘  
> 狀態：已製作正式 18 頁 PPTX，並以 Microsoft PowerPoint 2024 成功渲染為 PDF。下載：[PPTX](presentations/Smart_Warehouse_AI_Agent_Proposal.pptx)｜[PDF](presentations/Smart_Warehouse_AI_Agent_Proposal.pdf)。本檔保留逐頁內容與講稿來源。

> 所有實驗結果均為 **Not Run / Expected Outcomes**，不得在口頭報告中說成已觀測成果。

---

## Slide 1 — 封面

**重點**

- Smart Warehouse AI Agent
- 智慧倉儲單據辨識與庫存異常決策代理人
- AI Agent + Domain Knowledge + Data Analytics + Real-World Application
- 組員、課程、指導教師、日期：**需要人工填寫**

**建議圖表**：單據、資料庫、Agent、人工覆核四個圖示形成簡潔流程。

**報告講稿**：本專題不是只做 OCR 或聊天機器人，而是從倉儲單據出發，查詢庫存、套用規則、辨識異常、保留證據，並在高風險情況交由人員確認。

---

## Slide 2 — Research Motivation

**重點**

- 2025 Warehouse/DC Operations Survey：在 101 位合格受訪者中，87% 使用 WMS，但 51% 仍以人工方式蒐集生產力資料。
- 76% 使用 inventory accuracy 指標；調查樣本有限，不外推至全球。
- 單據數位化與可信決策之間仍有缺口。

**建議圖表**：三個大數字卡片 `87% / 51% / 76%`，下方註明來源與 n=101。

**報告講稿**：即使倉庫已使用 WMS，前端資料輸入與核對仍可能依賴人工。這代表導入系統不等於資料正確，也不等於異常能被解釋。

---

## Slide 3 — Problem Definition

**重點**

- 輸入：圖片／PDF、庫存 snapshot、品項主檔、歷史單據。
- 問題：版型變異、OCR error、缺欄、重複單據、負庫存、未知 SKU。
- 輸出需求：結構化欄位、異常、建議、evidence、human gate。
- Scope：recommendation-only，不直接寫正式 WMS/ERP。

**建議圖表**：Problem funnel：unstructured documents → conflicting data → risky decision。

**報告講稿**：真正問題不是「讀到多少字」，而是讀到的資訊是否足以支持安全的倉儲判斷。

---

## Slide 4 — Research Questions and Objectives

**重點**

- RQ1：Agent／Rules 是否提升重要欄位 Exact Match？
- RQ2：Agent 是否提升跨來源異常偵測？
- RQ3：evidence 與 human gate 是否降低錯誤自動通過？
- RQ4：改善是否值得 latency、RAM 與人工成本？
- 目標：可重現、可稽核、一般學生電腦可執行。

**建議圖表**：RQ → Metric 對照矩陣。

**報告講稿**：四個研究問題分別回答辨識、異常、安全與可行性，避免只展示 demo 而沒有可驗證研究問題。

---

## Slide 5 — Related Work and Research Gap

**重點**

- AI Technology：SROIE、DocVQA、AID-Agent、DocAgent、domain IE comparison。
- Warehouse Domain：IoT、inventory anomaly、AI picking、smart warehousing、Digital Twin。
- Existing Research：文件 AI 與倉儲 AI 各自成熟。
- Gap：缺少 document → inventory context → domain rules → evidence-backed decision 的輕量整合與公平 baseline。

**建議圖表**：兩個圓「Document AI」「Warehouse Intelligence」，交集標示本專題。

**報告講稿**：文件研究多停在抽取或問答，倉儲研究多假設資料已結構化；本專題研究兩者之間的決策連接層。

---

## Slide 6 — Five Expert Mindsets

**重點**

1. 流程與狀態守恆。
2. 唯一識別與端到端追溯。
3. 資料品質是 fitness for use。
4. 例外導向與風險分級。
5. 閉環校正與根因學習。

**建議圖表**：五邊形或環形圖，每個 mindset 對應一個設計元件。

**報告講稿**：這五個思維將系統從 OCR 工具轉為領域代理人。例如負庫存是 observation，不代表 Agent 已知道 root cause。

---

## Slide 7 — Three Professional Controversies

**重點**

- 高度自動化 ↔ Human-in-the-loop → 共識：risk-based automation。
- Deterministic Rules ↔ Learning Agent → 共識：hybrid design。
- RFID／即時 visibility ↔ 盤點／文件對帳 → 共識：多來源核對，沒有單一絕對真值。
- 未解問題：threshold、人工負荷、domain shift、成本效益。

**建議圖表**：三條左右拉鋸軸，中間標 Current Consensus。

**報告講稿**：我們不把爭論簡化成二選一；每項都區分已有共識與仍需本地資料回答的問題。

---

## Slide 8 — Ten Deep Questions

**重點**

1. 為何高 OCR accuracy 不等於正確決策？
2. 若文件與 snapshot 時間不同？
3. 自動通過率與危險錯放如何權衡？
4. OCR、barcode、主檔衝突時信誰？
5. 什麼是充分 evidence？
6. 為何保留 OCR + Rules baseline？
7. 為何使用 bounded planner？
8. 人工核准後發現錯誤怎麼辦？
9. 新版型低信心時是否降低 threshold？
10. 為何盤點差異不能直接定因？

**建議圖表**：2×5 question cards；報告時只深入第 1、3、4、7 題。

**報告講稿**：十題用 Why、What-if、Trade-off 與 Failure Case 檢查設計是否真的理解倉儲，而不是只會套模型。

---

## Slide 9 — Proposed Domain AI Agent

**重點**

- Planner：任務理解、tool selection、stop/escalate。
- Tools：OCR、parser、inventory/history query、analytics、rules。
- Reasoning：facts → conflicts/unknowns → evidence-backed rationale。
- Decision：severity × confidence × coverage × freshness。
- Human：approve、edit、reject、reprocess。

**建議圖表**：Agent loop，強調 allowlist、maximum steps、read-only data。

**報告講稿**：只有能根據中間結果選工具、補查或停止的部分稱為 Agent；OCR、SQL 和規則仍是普通可測試工具。

---

## Slide 10 — System Architecture

**重點**

- ① User Scenario → ② Query/Input → ③ Planner Agent。
- ④ Acquisition → ⑤ Analytics → ⑥ Domain Knowledge。
- ⑦ Decision → ⑧ Output/Interaction。
- SQLite 為預設；Google Sheets 為規劃中的 adapter。

**建議圖表**：直接使用 `architecture.md` Mermaid 圖，簡化字體後放大。

**報告講稿**：架構將 perception、analytics、rules、decision 與 interaction 分開，使每個錯誤可定位、每個模組可單獨驗證。

---

## Slide 11 — Flowchart and Failure Handling

**重點**

- Input → Processing → OCR → Validation → Analytics → Domain → Decision → Output。
- OCR retry once；缺欄／資料失效／規則衝突轉人工。
- Duplicate 與 inventory mismatch 保留不同 reason codes。
- Reprocess 沿用 trace ID，不覆寫先前紀錄。

**建議圖表**：使用 `flowchart.md` Mermaid，將正常路徑綠色、exception 紅色、human loop 橘色。

**報告講稿**：失敗不是空值成功。資料來源不可用與查無資料必須區分，否則可能把系統錯誤誤判成零庫存。

---

## Slide 12 — Algorithm 1

**重點**

- Task understanding and bounded plan。
- OCR／retry、schema validation、read-only queries。
- Duplicate、reconciliation、statistics、rules。
- Confidence、evidence coverage、risk、human confirmation。
- `ASSERT_NO_WMS_WRITE_OCCURRED`。

**建議圖表**：擷取 `algorithm.md` 01–29、43–59、62–91 三段；旁邊放三個 invariants。

**報告講稿**：演算法的重點不是 92 行本身，而是每個 exit condition 都 fail-safe，並且原型沒有自動寫正式庫存的能力。

---

## Slide 13 — MVP Implementation and Demo Path

**重點**

- Python 3.11、Streamlit、SQLite、Pandas。
- 已有 bounded planner、synthetic OCR、parser、database、rules、audit。
- 6 個 automated tests 已通過；僅代表合成 fixture。
- 真實 image OCR、scanned PDF、Google Sheets、LLM provider 尚未完成。

**建議圖表**：Implemented／Partial／Not Implemented 三欄狀態圖。

**報告講稿**：這頁要誠實區分「程式存在」「實際測過」和「仍需外部依賴」，不把 smoke test 說成完整使用者驗收。

---

## Slide 14 — Dataset Design

**重點**

- Public pretest + anonymous/synthetic warehouse documents + paired snapshots。
- 目標 300–500 張、3 類文件、5 種版型；尚未取得，Not Run。
- Group split：vendor + template，60/20/20，seed 20261024。
- 防止同原稿與增強版跨 split；test manifest freeze。

**建議圖表**：資料三層金字塔與 split 示意。

**報告講稿**：公開收據資料只驗證 pipeline，不代表本地倉儲。真正結論必須來自配對庫存與異常標註資料。

---

## Slide 15 — Three Baselines

**重點**

| B0 | B1 | B2 |
|---|---|---|
| 人工輸入與核對 | OCR + Fixed Rules | OCR + Domain AI Agent |
| 完整人工時間 | 固定 pipeline | adaptive tool plan |
| Operational reference | Non-agent control | Proposed method |

- 三者使用相同 test documents 與 database snapshots。
- B1/B2 共用 OCR、parser、rules、thresholds、hardware。

**建議圖表**：三條平行 pipeline，將共同元件對齊。

**報告講稿**：B1 是關鍵控制組；如果只跟純 OCR 比，無法知道進步是來自規則、查詢還是 Agent planning。

---

## Slide 16 — Evaluation Metrics and Procedure

**重點**

- Character Accuracy / CER。
- Important-field EM、Document EM。
- Anomaly Precision、Recall、macro-F1。
- Duplicate Accuracy + duplicate F1。
- Mean/median/P95 time、human intervention。
- Tool selection precision/recall、safe tool rate、task completion。
- Paired comparison、bootstrap 95% CI；results currently Not Run。

**建議圖表**：Metric → RQ → failure cost matrix；右下角放空白結果表縮圖。

**報告講稿**：所有方案按同一 test manifest 配對比較。Agent 不能只以回答完成為成功，還必須選對工具、沒有越權、證據完整且 disposition 正確。

---

## Slide 17 — Expected Contributions and Feasibility

**重點**

- C1：把 OCR 問題重構為可測量的 domain decision agent。
- C2：evidence-first、human-gated、recommendation-only architecture。
- C3：公平 B0/B1/B2 protocol 與 safety metrics。
- C4：學生電腦可執行、可替換 OCR/LLM 的 open-source MVP。
- Expected：B2 可能改善跨來源異常與 auditability，但付出 latency／complexity；尚待實驗。

**建議圖表**：Contribution × Evidence × Deliverable 表。

**報告講稿**：預期貢獻不是宣稱模型已優於所有方法，而是提出能被反駁、能被量測、失敗時可安全停止的整合方案。

---

## Slide 18 — References, Status, and Next Steps

**重點**

- 核心來源：DocAgent 2025、AID-Agent 2025、IoT warehouse review 2025、AI picking 2025、smart warehousing 2026、NIST、GS1。
- 完整 References 見 `proposal.md` 與 `deep_research.md`。
- Next：教師確認 protocol → data card/annotation → pilot 30–50 → freeze → B0/B1/B2 experiment。
- 尚未執行：正式 dataset、人工 baseline、真實 OCR、效能及統計分析。

**建議圖表**：四階段 roadmap；底部 QR/link 指向 repository（URL 需要人工填寫）。

**報告講稿**：目前完成 Proposal、Deep Research、Design、MVP synthetic tests 與完整實驗設計；下一個 gate 是取得合規資料並由教師確認評估方案，而不是先填入漂亮數字。

---

## Export and Validation Notes

- 產生工具：`python-pptx`；可重現腳本為 `scripts/build_proposal_pptx.py`。
- 架構圖與流程圖以 PowerPoint 原生 shapes/connectors 重繪，可在 PowerPoint 中編輯；不是把 Markdown 文字整頁貼入。
- 2026-10-31 已由 Microsoft PowerPoint 2024 開啟並匯出 18 頁 PDF，確認檔案可渲染。
- 投影片仍保留「組員、課程、指導教師」人工填寫欄位；正式口試前需依課程資料補齊。
- 正式實驗未執行，簡報內所有結果均標示 `Not Run` 或 `Expected Outcomes`。

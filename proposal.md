# Final Project Proposal

## Smart Warehouse AI Agent — 智慧倉儲單據辨識與庫存異常決策代理人

> 文件版本：v0.1（第一至第三部分）  
> 更新日期：2026-10-24  
> 文件狀態：Proposal；尚未執行模型訓練或正式實驗。本文所有未來效能敘述均屬 **Expected Outcomes**，不得解讀為 Observed Results。  
> 查證聲明：文獻以出版社、正式論文頁面、官方資料集或標準組織為優先。僅取得摘要／metadata 者已在文獻表標註，未據此推論全文未揭露之細節。

---

# 第一部分　Abstract

### A. Attention Getter

倉儲數位化並未消除資料品質與人工處理問題。2025 Warehouse/DC Operations Survey 對 101 位合格倉儲與物流從業者的調查顯示，87% 受訪單位已使用 Warehouse Management System（WMS），但仍有 51% 以人工方式蒐集生產力資料；同一調查中，76% 將 inventory accuracy 作為管理指標，而平均 SKU 數由前一年的 7,790 增至 9,565 [11]。此為特定產業調查而非全球母體統計，仍顯示系統普及與資料自動化之間可能存在落差。另一方面，2025 年倉儲與庫存 IoT 系統性文獻回顧指出，既有研究多集中於理論框架與演算法，實際應用相對不足 [6]。因此，倉儲問題不只是「能否讀到字」，而是能否把單據、庫存紀錄與作業規則整合為可追溯且可由人員覆核的決策。

### B. But

傳統 Optical Character Recognition（OCR）主要將影像轉換為文字與座標，無法單獨判定某筆收貨是否重複、出庫後是否形成負庫存、料號是否存在主檔，或批號與效期是否符合特定倉儲政策。SROIE 將收據處理拆分為文字定位、OCR 與關鍵資訊抽取，說明辨識與欄位理解本來就是不同層次的任務 [4]；DocVQA 亦顯示，涉及文件結構理解的問題仍比單純擷取更具挑戰 [5]。固定規則雖能檢查已知格式，卻常依賴預設欄位與單一路徑；面對低品質影像、未見版型、缺欄與跨來源衝突時，容易停止於錯誤訊息，或產生缺乏上下文的警示。

### C. Cure

本研究提出 **Smart Warehouse AI Agent**，定位為具有限責任與人工監督的 Domain AI Agent。系統接收入庫單、出庫單或盤點單影像，以及去識別化的庫存快照與品項主檔，先取得文件證據，再規劃所需工具、查詢庫存、套用倉儲規則、判斷異常，最後輸出「建議通過、要求補件、人工覆核或暫停處理」等建議。系統在原型階段不直接修改正式 WMS／ERP，也不自動核准高風險交易。

### D. Development

系統以有限狀態 Planner 統籌 OCR Tool、結構化 Parser、唯讀 Inventory Query、版本化 Rule Engine 與 Evidence Store。Reasoning 採 evidence-first 原則，只能根據文件 bounding box、OCR 片段、庫存 row ID 與 rule ID 形成異常假設；Decision 則依 risk、field confidence 與 evidence coverage 啟動 Human-in-the-loop。此設計參考 AID-Agent 將 OCR、LLM 與 domain/task-specific tools 結合的方向 [2]，以及 DocAgent 透過工具查詢與 reviewer cross-check 提升文件回答可靠性的作法 [1]，但縮小為一般學生電腦可開發、可重播且 recommendation-only 的倉儲決策原型。

### E. Experiments

資料規劃分為三層：（1）SROIE 與 DocVQA 等公開資料用於 OCR／文件理解 pretest；（2）預計建立 300–500 張、至少三類單據與五種版型的去識別化中英倉儲單據；（3）建立與單據配對的 CSV／SQLite 庫存快照及具固定 seed 的異常情境。若實際資料量未達目標，將報告實際樣本數及限制。實驗以相同 OCR、資料切分與硬體比較 B0 純 OCR、B1 OCR + Rules、B2 OCR + Agent。評估包含 CER／WER、欄位 Precision／Recall／F1 與 Exact Match、異常 macro-F1／PR-AUC／誤報率／漏報率、錯誤自動通過率、適當升級率、evidence coverage、trace replay success、median／P95 latency 與峰值 RAM，並進行未見版型、影像劣化及元件消融實驗。

### F. Expected Outcomes

**Expected Outcomes：** 本研究預期建立一套由「文件辨識」延伸至「有證據的倉儲異常建議」之可重現架構；B2 預期在跨資料來源異常的召回、證據完整性及高風險案件升級方面優於 B0 與 B1，但可能增加延遲、記憶體與系統複雜度。預期學術貢獻是提出可測量的 OCR—Rules—Agent 比較框架；實務貢獻則是提供不直接寫入正式庫存、保留人工責任與稽核軌跡的學生級可行原型。上述均為待實驗驗證之預期，本文不宣稱已取得任何效能提升。

---

# 第二部分　Introduction

## 2.1 Attention Getter

智慧倉儲的核心資產不只是貨架與自動化設備，也是能否反映實物流動的可靠資料。2025 Warehouse/DC Operations Survey 顯示，在其 101 位合格受訪者中，WMS 使用率達 87%，但以人工方式蒐集生產力資料者仍達 51%；76% 使用 inventory accuracy 指標，且受訪倉儲的平均 SKU 數增加至 9,565 [11]。這組結果不可外推至所有國家或產業，但它揭示一個具體矛盾：企業可能已具備 WMS，前端文件輸入、資料核對與指標生成仍依賴人工。當 SKU、供應商版型與作業量增加，單一錯字、漏欄或重複單據可能沿著收貨、上架、揀貨及出貨流程擴散。

2025 年 IoT 倉儲系統性回顧也指出，既有研究偏重理論框架與演算法，真實部署仍不足 [6]；2026 年智慧倉儲回顧則進一步認為，技術、SKU 流程階段、階層決策與 KPI 之間仍缺少統一整合 [9]。這意味著「採用 AI」不等於完成倉儲決策閉環：系統仍需知道資料從何而來、規則適用於何種作業、何時應停止自動化，以及由誰承擔最終確認責任。

## 2.2 Background

倉儲單據通常同時具有視覺版面、文字、表格與業務語意。OCR 可輸出字元及位置；Key Information Extraction（KIE）則把文字映射為單號、日期、SKU、數量、單位、批號及效期等欄位。SROIE 將 scanned receipt processing 分成文字定位、文字辨識及關鍵資訊抽取三項任務 [4]，DocVQA 則把文件理解定義為對文件影像回答問題，並收錄 12,000 餘張文件影像與 50,000 個問題 [5]。兩者提供文件 AI 的可比較基礎，但並非臺灣倉儲單據或庫存決策資料，不能直接代表本專題的 domain performance。

近年的 agentic document AI 使模型不再只執行一次性辨識。AID-Agent 以中央排程結合 OCR、LLM、表格抽取與 domain knowledge tool，並在 44 份人工標註的工業技術文件上進行案例驗證 [2]。DocAgent 則先建立文件樹狀綱要，再讓 agents 動態查詢內容並由 reviewer agent 交叉檢查答案 [1]。這些研究支持「規劃—工具—驗證」的方向，但其任務主要是複雜文件抽取或長文件問答，尚未直接回答倉儲單據與庫存快照如何共同形成異常處置建議。

倉儲領域方面，收貨作業包含卸貨、檢查品質與數量差異，以及更新庫存；order picking 則需取得正確品項與數量 [8]。GS1 Logistic Label Guideline 規範 SSCC、GTIN、batch/lot 與日期等識別資訊，並指出 master data alignment、掃描與保存追溯關係的重要性 [10]。因此，本研究所稱 Domain Knowledge 不是讓語言模型自由生成「常識」，而是把可查證標準、專題政策與明確標示的研究假設轉成有 rule ID、版本、severity 與來源的規則。

## 2.3 Problem

本研究聚焦以下可操作問題：倉儲人員收到影像或 PDF 單據後，需要辨識欄位、對照品項主檔與庫存快照、找出數量或識別異常、保留原始證據，並在不確定時要求補件或人工覆核。純 OCR 只提供文字；一般 WMS 假設輸入已結構化且正確；獨立異常偵測模型則通常從既有數值序列或表格開始。三者之間缺少一個安全且可稽核的連接層。

具體錯誤情境包括：（1）同一供應商與單據類型下出現重複單號；（2）OCR 將相似 SKU 字元混淆；（3）出庫數量高於可用量；（4）單據明細合計與表頭合計不一致；（5）受批號或效期管理的品項缺少必要欄位；（6）單據、主檔與庫存列互相矛盾。此類問題需要同時取得視覺證據、資料庫紀錄與作業規則，不能由單一分類器或聊天介面完整處理。

## 2.4 Existing Limitations

現有方法具有五項限制。第一，OCR error 會傳遞至欄位抽取與後續規則，且低解析、折痕、旋轉與複雜表格會增加錯誤；SROIE 所列的紙張、印刷、掃描與版面問題即反映此現象 [4]。第二，固定 rules 對已知欄位有效，卻不會自行取得缺少的上下文，也難以處理未見版型。第三，LLM 或 agent 雖具彈性，仍可能產生 unsupported claims、工具誤用、成本與延遲；AID-Agent 亦把複雜表格、跨頁關聯與成本列為挑戰 [2]。第四，倉儲 AI 研究常聚焦揀貨路徑、IoT、Digital Twin 或數值異常模型 [6]–[9]，對非結構化單據到具證據決策的端到端問題著墨較少。第五，若缺少 human gate 與 audit log，即使平均準確度良好，少數高風險錯誤仍可能被自動放行。NIST AI RMF 強調 human-AI roles、透明性、可追溯性與持續性風險管理 [12]，故本專題不以全自動化為目標。

## 2.5 Innovation

本專題創新性不建立在「發明新的 OCR 模型」，而在可測量的系統整合與責任邊界：

1. **由 OCR 升級為有限責任 Agent。** Planner 僅能在 allowlist 內調用 OCR、Parser、唯讀庫存查詢、Rule Engine 與 Evidence Store，並設 maximum steps、single retry 與 stop condition。
2. **Evidence-first warehouse reasoning。** 每一異常與建議必須引用影像 bounding box、OCR span、inventory row ID 或 rule ID；缺少證據即不得形成自動通過建議。
3. **版本化 Domain Knowledge。** 將 GS1 識別概念、倉儲數量一致性與專題政策寫成可測試規則，並清楚區分標準、組織政策及研究假設。
4. **Risk × Confidence Human Gate。** 不只以 OCR confidence 判斷，而是綜合異常 severity、欄位信心、來源衝突與 evidence coverage 決定人工覆核。
5. **公平三層 baseline。** 在相同 OCR、schema、split 與硬體下比較純 OCR、OCR + Rules、OCR + Agent，評估 agent orchestration 的實際增益與成本。

本研究不宣稱上述組合為全球首創；是否具有文獻上的新穎性，仍須在完整系統性檢索後確認，現階段此項標示為**待查證**。

### Research Questions

- **RQ1：文件理解效能。** 在相同 OCR 與資料切分下，OCR + Rules 與 OCR + Agent 是否能比純 OCR 提升倉儲關鍵欄位的 Precision、Recall、F1 與 Exact Match？
- **RQ2：異常判斷效能。** Agent 使用唯讀庫存查詢與版本化 Domain Rules 後，是否能比非 Agent baseline 更準確偵測重複單據、未知 SKU、數量不一致、預估負庫存及批號／效期缺漏？
- **RQ3：決策安全與可追溯性。** Evidence pointer、risk × confidence policy 與 Human-in-the-loop 是否能降低錯誤自動通過率，並提高 evidence coverage、適當升級率與 trace replay success？
- **RQ4：可行性與代價。** 上述改善是否值得 Agent 帶來的 median／P95 latency、RAM、工具呼叫數與可能 API 成本？

### Research Objectives

本研究目標為：

1. 建立可處理入庫、出庫或盤點單的版本化 document schema 與 evidence model。
2. 在一般學生電腦上實作由 Planner、Tools、Domain Knowledge、Reasoning、Decision 與 Human Review 構成的最小可行 Agent。
3. 建立去識別化中英倉儲單據、庫存快照及可重現異常注入方法，並防止同版型資料洩漏至不同 split。
4. 在公平控制條件下比較 B0、B1、B2，除準確度外，同時衡量安全、稽核與資源成本。
5. 形成可由教師、倉管人員或研究者追查每項決策依據的 append-only audit trail。

## 2.6 Contributions

預期貢獻如下，均須由後續實驗驗證：

- **C1 — Research framing：** 將倉儲單據辨識轉換為跨文件、庫存與規則的 Domain AI Agent 問題，提出四項 RQ 與可量測指標。
- **C2 — System design：** 提出 evidence-first、recommendation-only、human-gated 的 Agent 架構，使辨識錯誤與決策權限可被隔離。
- **C3 — Evaluation protocol：** 提供三種 baseline、held-out template、影像劣化、ablation 與 decision-safety metrics。
- **C4 — Reproducible artifact：** 預計提供 Python、SQLite、開源 OCR、版本化規則、資料卡、設定與測試；敏感或未授權資料不公開。

---

# 第三部分　Related Work

## 3.1 Review Scope and Evidence Policy

本節選取 10 篇核心研究文獻，其中 5 篇屬 AI Technology（[1]–[5]），5 篇屬 Warehouse Domain Knowledge（[6]–[9]、[13]），比例各半。優先納入 2025–2026 年正式出版研究；較早的 SROIE 與 DocVQA 僅用作 benchmark 基礎。另以 GS1 Guideline [10] 補充領域標準、2025 產業調查 [11] 說明實務背景、NIST AI RMF [12] 支持可信任與人工監督設計，三者不列入上述十篇研究文獻的比例計算。

證據狀態分為：（a）**全文可取得／已檢視**：可摘要方法、資料與作者明示限制；（b）**僅摘要與 metadata 已核對**：只陳述摘要明示內容，不推論全文；（c）**官方標準全文已檢視**。截至 2026-10-24，[7] 的 IEEE 頁面僅能取得摘要及部分頁面，其作者名單與全文實驗細節標示為**待查證**。

## 3.2 AI Technology

### 3.2.1 OCR、KIE 與 Document Understanding

Huang et al. 建立 SROIE competition，以 1,000 張掃描收據定義文字定位、OCR 與 key information extraction 三項任務 [4]。此研究的重要性在於提供標準化資料與評估程序，並使「辨識文字」與「抽取業務欄位」可被分別量測。然而，SROIE 的文件為收據，關鍵欄位主要是公司、日期、地址與總額；它不包含倉儲庫存快照、SKU 主檔、批號規則或決策 ground truth，故只適合本研究的 OCR/KIE pretest。

Mathew et al. 提出的 DocVQA 包含 12,000 餘張文件影像及 50,000 個人工標註問題，將文件處理提升為目的導向的 visual question answering [5]。論文指出涉及文件結構的問題仍存在明顯挑戰。DocVQA 能測試文字、影像與版面聯合理解，但答案通常是文件中的文字片段，並未涵蓋對外部庫存狀態的查詢或風險決策。

Principe et al. 以不動產拍賣文件比較人工標註、rule-based methods 與 LLM-based information extraction，討論 accuracy、scalability 與 cost-efficiency 的權衡 [3]。其價值在於直接支持本專題採用多 baseline、避免預設 LLM 必然優於 rules；但 domain 為不動產文件，且研究問題是資訊抽取，不是倉儲異常處置。

### 3.2.2 Agentic Document AI

Li, Conen, and Aller 提出的 AID-Agent 將 OCR 與 LLM agent 結合，由可客製 toolset 支援表格重建、domain knowledge 與格式驗證；論文以 44 份人工標註的工業技術 PDF 作案例研究 [2]。它顯示 domain-specific tool 可補足通用 OCR/LLM 對複雜表格與專業實體的不足，也提醒長文件與 multimodal LLM 具有成本負擔。其資料規模小且任務為技術文件資訊整合，未評估倉儲 inventory anomaly、錯誤自動通過或人工決策責任。

Sun et al. 的 DocAgent 針對長篇多模態文件，先建立結構化綱要，再由 agents 動態查詢頁面內容，並以 reviewer agent 交叉檢查回答 [1]。此研究支持本專題使用 planner、tool interface、review 與跨來源驗證；但 DocAgent 面向長文件 QA，其 benchmark 與 success criteria 不等同於單據欄位精確度、庫存一致性或倉儲風險分級。

## 3.3 Warehouse Domain Knowledge

### 3.3.1 Warehouse Data、IoT 與智慧化架構

Puga Mendoza, Caballero Chávez, and Torres Mendoza 回顧 2017–2023 年 IoT 在倉儲與庫存管理的應用，指出研究主要集中於少數理論框架與演算法，實際應用仍不足 [6]。該結論支持本專題以可執行 MVP 與真實工作流程作為目標；但其回顧涵蓋 IoT 架構，不專門處理 OCR 或 document agents。

El Kadmiri et al. 以兩組 PRISMA review 建構 2026 智慧倉儲框架，整合 Cyber-Physical Systems、Digital Twins、Collaborative Robots、Deep Reinforcement Learning、SKU flow phases、階層層級與 KPI [9]。該文強調 monitoring、optimization、decision support 與 human-centricity 需在同一架構內考量，並指出 interoperability、cybersecurity 與硬體資源仍是缺口。它提供本研究定義倉儲流程及 KPI 的高層脈絡，但本身是 conceptual framework，沒有使用倉儲單據影像建立異常決策 agent。

Alam et al. 於 2026 年回顧 AI-enhanced Digital Twin 在 warehouse logistics 的應用，涵蓋 path planning、task allocation、inventory management、storage assignment、AGV、IoT 與 anomaly detection [13]。作者同時指出經濟影響、動態環境適應、collaborative robots 及 reverse logistics 等議題仍需更多研究。該文說明智慧倉儲需要跨來源資料與決策支援，但研究單位是 Digital Twin 生態系，而非從原始單據建立可稽核異常建議。

### 3.3.2 倉儲 AI、異常與人機流程

2025 IEEE conference paper〈Research on abnormal inventory detection algorithm in warehouse management system〉提出 improved local anomaly factor、attention recurrent neural network 與 Bayesian model averaging 的融合架構；出版者摘要稱其在含 12,358 個 SKU 的真實電商庫存資料上獲得 F1 87.3% [7]。由於目前僅核對 IEEE 摘要與 metadata，作者、資料切分、異常定義、比較方法及 production claim 均為**待查證**，本研究不把 87.3% 當作可直接比較的 baseline。該文仍顯示 inventory anomaly 可以被定義為可測量分類任務，但其輸入是庫存資料，而非含 OCR error 的原始單據。

Rad et al. 以 customer order data、simulation 及倉儲人員、ERP developer、AI developer 訪談研究 AI-based batch order picking [8]。研究報告 AI 系統可減少揀貨距離與時間，同時指出組織與實施挑戰會限制系統充分利用。它提醒本專題不能只報模型準確度，還要評估作業適配、人工角色與可行性；但 order-picking optimization 與本研究的 document-to-decision 任務不同。

GS1 Logistic Label Guideline 規範物流單元識別及資料交換，要求以 SSCC 支援追溯，並涵蓋 GTIN、count、batch/lot 及 production/best-before/expiry dates 等 Application Identifiers；規範亦強調 master data alignment、條碼掃描、標籤驗證與保存 SSCC 關係 [10]。這些內容可作為欄位 schema 與 evidence linkage 的領域依據，但不是所有品項都強制具有相同欄位；實際是否管理批號或效期仍須由品項主檔與組織政策決定，相關門檻現階段標為**待查證**。

## 3.4 Article Summary Table

| Ref. | Year | Problem | AI Method | Domain Knowledge | Dataset | Findings | Limitation |
|---|---:|---|---|---|---|---|---|
| [1] AI | 2025 | 長篇多模態文件難以在有限 context 中可靠問答 | Tree outline、multi-agent、interactive retrieval、reviewer agent | 文件結構與跨來源核對 | 兩個 long-context document benchmarks | 作者報告其方法優於競爭 baselines，並以 reviewer 增強可靠性 | 面向長文件 QA，非倉儲交易；未評估 inventory rules 或 human approval |
| [2] AI | 2025 | 複雜表格、跨頁資訊及專業實體使一般 OCR/LLM 抽取失敗 | LLM agent + OCR + customizable tools + validator | 工業技術文件欄位、格式與專業知識工具 | 44 份人工標註工業技術 PDF | domain/table tools 可支援複雜文件整合；作者報告優於其 conventional baselines | 小型單一案例；未處理倉儲異常、安全決策及正式庫存 |
| [3] AI | 2025 | Domain-specific IE 應如何平衡準確度、擴展性與成本 | LLM、rule-based 與 human annotation 比較 | 不動產拍賣文件 | Real-estate case study；樣本細節見全文 | 顯示方法選擇存在 performance、maintainability、cost trade-off | Domain 非倉儲；聚焦抽取，沒有外部工具決策 |
| [4] AI | 2019 | 缺少標準化的掃描收據 OCR/KIE benchmark | OCR、text localization、KIE competition baselines | 收據公司、日期、地址、總額 | 1,000 張 scanned receipts | 建立三任務與標準評估程序 | 語言／地區／文件類型有限；無 SKU、庫存或決策標註 |
| [5] AI | 2021 | 模組式 OCR/KIE 不等於整體文件理解 | Document Visual Question Answering baselines | 文件版面與問題語意 | 12,000+ images、50,000 questions | 結構相關問題仍具挑戰，提供公開 benchmark | 答案多為文件 span；沒有倉儲外部狀態與風險動作 |
| [6] Warehouse | 2025 | IoT 倉儲／庫存研究分散，缺少趨勢整理 | 系統性文獻回顧與分類分析 | Warehouse、inventory、IoT architecture | 2017–2023 年納入文獻 | 研究偏重理論與演算法，實際應用較少 | 回顧而非部署實驗；未聚焦文件 AI |
| [7] Warehouse | 2025 | 電商倉儲多類 inventory anomaly 難以用單一模型識別 | Improved local anomaly factor + attention RNN + Bayesian model averaging | Inventory temporal、多維與關聯特性 | 摘要稱真實電商資料 12,358 SKUs | 摘要報告 F1 87.3% | **僅摘要／metadata 已核對；作者、split、異常定義與全文結果待查證**；輸入非單據影像 |
| [8] Warehouse | 2025 | AI-based batch order picking 的效益、挑戰與成功因素 | AI optimization、simulation、quantitative + interviews | Receiving、picking、ERP 與員工作業 | Customer order data、simulation、stakeholder interviews | 作者報告降低揀貨距離與時間，亦存在 adoption challenges | 單一實務脈絡；任務為揀貨最佳化，非單據辨識與異常判斷 |
| [9] Warehouse | 2026 | 智慧倉儲技術、流程層次與 KPI 缺乏整合 | SLR + exploratory literature-data analysis + conceptual framework | Inbound/storage/outbound、KPI、resilience、sustainability | 2015–2025 文獻；無 operational dataset | 整合 CPS、DT、cobots、DRL、SKU flows 與 KPI | 概念性框架；未提供 document-to-decision 實驗系統 |
| [13] Warehouse | 2026 | AI、Digital Twin、IoT 與倉儲物流最佳化研究分散 | AI-enhanced Digital Twin literature review | Path planning、task allocation、inventory、storage assignment | 既有研究文獻；無單一 operational dataset | 彙整 DT、AI、IoT、AGV、robotics 與 anomaly detection 的應用方向 | 回顧研究；經濟效益、動態環境、協作機器人與 reverse logistics 仍有缺口；未處理 document agent |

> 表中「Findings」只重述作者或官方來源明示內容。跨研究的數值不可直接比較，因任務、資料、split 與指標定義不同。

## 3.5 Existing Research → Limitations → Research Gap → Our Project

### Existing Research

既有文件 AI 已從 OCR/KIE benchmark [4]、document VQA [5]，發展至能分解任務、調用工具與交叉檢查的 document agents [1], [2]；domain-specific IE 研究也顯示 human、rules 與 LLM 各有準確度、維護與成本權衡 [3]。另一方面，智慧倉儲研究涵蓋 IoT、inventory anomaly detection、AI picking、Digital Twin 與 KPI [6]–[9], [13]；GS1 規範則提供物流識別與追溯基礎 [10]。

### Limitations

兩條研究路徑多半平行發展。文件 AI 主要輸出文字、欄位或答案，通常不讀取倉儲即時／快照狀態，也不依 domain risk 決定人工升級；倉儲 AI 多以已結構化的訂單、感測器或 inventory series 為輸入，通常假設資料已正確進入系統。兩者皆可能未完整量測 evidence coverage、錯誤自動通過與 trace replay。公開 benchmark 亦缺少中英倉儲單據、配對庫存、規則命中及人工決策標註。

### Research Gap

因此，本研究識別的缺口是：**缺少一個能由非結構化倉儲單據出發，主動取得庫存資料、套用版本化專業規則、為異常建議保留逐項證據，並依風險與信心交由人工確認的輕量 Domain AI Agent，以及對此 Agent 相較純 OCR 與 OCR + Rules 的公平評估。** 此缺口目前由本節文獻綜合推論而得；是否已有完全相同之系統，仍須擴充資料庫與關鍵詞進行系統性檢索，故「全球尚無同類系統」之命題標為**待查證**。

### Our Project

Smart Warehouse AI Agent 將以有限狀態 Planner 串接 OCR、schema parser、唯讀 inventory query、rule engine 與 evidence store。系統不保存或要求模型隱藏思考過程，而輸出結構化 facts、rule hits、conflicts／unknowns、reason codes 與 evidence IDs；高風險、低信心、矛盾或證據不足案件必須進入 Human Review。研究將在共同資料與條件下比較 B0、B1、B2，並同時衡量 document accuracy、anomaly performance、decision safety、auditability 與 feasibility。此設計旨在回答「Agent 是否帶來可驗證的決策價值」，而非只展示一個能對話的介面。

---

# 第四部分　Deep Research

完整研究內容、雙方證據、20 項來源與待查證紀錄收錄於 [deep_research.md](deep_research.md)。本節將其整合為 Proposal 的系統設計依據。

## 4.1 五個核心思維模式

| 核心思維 | 對本專題的意義 | 系統落點 |
|---|---|---|
| 流程與狀態守恆 | 庫存是收貨、移庫、揀貨、出貨及盤點事件形成的狀態，不是孤立數字 | `InventoryEvent`、數量／單位守恆、event-time 與 snapshot-time check |
| 唯一識別與端到端追溯 | 相似品名不能取代 GTIN、SSCC、SKU、batch 與 evidence provenance | identifier hierarchy、禁止 fuzzy auto-replace、欄位 evidence pointer |
| 資料品質的 fitness for use | 高 OCR 平均分不代表關鍵欄位、跨來源一致性或時效足以決策 | 分層 confidence、critical-field threshold、freshness 與 consistency reason codes |
| 例外導向與風險分級 | 自動化應處理低風險、證據完整案件；人的注意力保留給例外 | `severity × confidence × coverage × freshness` human gate |
| 閉環校正與根因學習 | 修正帳面差異不等於消除成因，必須保留錯誤、修正與再發資訊 | append-only audit、review feedback、root-cause taxonomy、replay regression |

## 4.2 三項關鍵專業爭論

1. **高度自動化 ↔ Human-in-the-loop：** 文件 agents 與 AI picking 顯示自動化潛力，但 NIST 風險框架要求依情境明確配置人工監督。現階段共識採 risk-based automation；可接受錯誤率與人工負荷仍待本地驗證。
2. **Deterministic Rules ↔ Learning-based Agent：** 規則適合 schema、識別格式、數量約束及權限；模型適合視覺變異與非結構化語意。Proposal 採 hybrid design，規則不得由 LLM 自行生成為正式政策。
3. **即時感測／RFID ↔ 盤點與單據對帳：** field studies 顯示 RFID visibility 可改善部分情境的 inventory accuracy，但 tag 漏讀與流程錯誤仍會形成 invisible inventory。系統因此把感測、文件、WMS 與 physical verification 視為可互相核對的來源，而非單一真值。

## 4.3 十個深度理解問題的設計結論

Deep Research 以 Why、What-if、Trade-off、Failure Case、Evidence、Comparison、Design Decision 與 Real-world Scenario 分析十題，包括：OCR 與交易正確性的差異、時間基準衝突、auto-pass threshold、識別來源衝突、充分證據、baseline 公平性、有限狀態 Planner、事後更正、新版型 drift，以及盤點差異的多重成因。其共同結論如下：

- 異常 observation 與 root-cause hypothesis 必須分開。
- 來源衝突不得 silent overwrite；應保留 candidates 與 evidence IDs。
- B0／B1／B2 必須共用 OCR、schema、split 與硬體，另以 ablation 歸因 Agent 增益。
- 新版型及影像劣化應提高監督，不得為維持 throughput 直接降低 threshold。
- 人工核准與後續 correction 均須追加紀錄；原型維持 recommendation-only。

## 4.4 轉換為 Domain Rules、Planning 與 Decision Logic

Deep Research 已轉換為十項初始規則：identifier priority、duplicate history check、quantity/unit validity、snapshot freshness、negative-stock escalation、conditional batch/expiry requirement、evidence integrity、risk-based human gate、append-only correction 及 unseen-template quarantine。Planner 因此依序執行：

`Validate Input → Extract Evidence → Normalize/Validate → Check Freshness → Query Context → Reconcile → Assess Evidence → Decide/Escalate → Append Trace`

任何 missing critical field、unsupported claim、high severity、source conflict、out-of-distribution 或 evidence coverage 不足，均不得產生自動通過；具體 threshold、效期天數、snapshot 最大年齡及可接受 false auto-accept rate 屬組織政策，目前標為**待查證**。完整 rule table、十題分析及 references 見 [deep_research.md](deep_research.md)。

---

# References

[1] L. Sun, L. He, S. Jia, Y. He, and C. You, “DocAgent: An Agentic Framework for Multi-Modal Long-Context Document Understanding,” in *Proceedings of EMNLP 2025*, pp. 17701–17716, 2025. DOI: [10.18653/v1/2025.emnlp-main.893](https://doi.org/10.18653/v1/2025.emnlp-main.893). 全文可取得／已檢視。

[2] B. Li, J. Conen, and F. Aller, “AID-Agent: An LLM-Agent for Advanced Extraction and Integration of Documents,” in *Proceedings of the 1st Workshop for Research on Agent Language Models (REALM 2025)*, pp. 80–88, 2025. [ACL Anthology](https://aclanthology.org/2025.realm-1.6/). 全文可取得／已檢視；ACL 頁面未列 DOI，故不填寫 DOI。

[3] R. A. Principe, M. Viviani, and N. Chiarini, “Enhancing Information Extraction with Large Language Models: A Comparison with Human Annotation and Rule-Based Methods in a Real Estate Case Study,” in *Proceedings of the 5th Conference on Language, Data and Knowledge*, pp. 243–254, 2025. [ACL Anthology](https://aclanthology.org/2025.ldk-1.25/). 正式出版 metadata 與摘要已核對；本文未據此延伸未核對的實驗數值；ACL metadata 未列 DOI。

[4] Z. Huang, K. Chen, J. He, X. Bai, D. Karatzas, S. Lu, and C. V. Jawahar, “ICDAR2019 Competition on Scanned Receipt OCR and Information Extraction,” in *2019 International Conference on Document Analysis and Recognition (ICDAR)*, pp. 1516–1520, 2019. DOI: [10.1109/ICDAR.2019.00244](https://doi.org/10.1109/ICDAR.2019.00244). 正式論文與 dataset metadata 已核對。

[5] M. Mathew, D. Karatzas, and C. V. Jawahar, “DocVQA: A Dataset for VQA on Document Images,” in *2021 IEEE Winter Conference on Applications of Computer Vision (WACV)*, pp. 2200–2209, 2021. DOI: [10.1109/WACV48630.2021.00225](https://doi.org/10.1109/WACV48630.2021.00225). [官方資料集頁面](https://site.docvqa.org/datasets/docvqa). 全文可取得／已檢視。

[6] A. Puga Mendoza, J. L. Caballero Chávez, and R. Torres Mendoza, “Applications and Methodologies of Internet of Things in Warehouses and Inventory Management: A Systematic Literature Review,” *Procedia Computer Science*, vol. 253, pp. 1236–1245, 2025. DOI: [10.1016/j.procs.2025.01.185](https://doi.org/10.1016/j.procs.2025.01.185). 正式出版 metadata、摘要與會議作者資料已核對；本文未假稱已逐頁審讀全文。

[7] 作者名單**待查證**, “Research on Abnormal Inventory Detection Algorithm in Warehouse Management System,” in *2025 International Conference on Artificial Intelligence and Engineering Management (ICAIEM)*, 2025. DOI: [10.1109/ICAIEM66060.2025.11139221](https://doi.org/10.1109/ICAIEM66060.2025.11139221). 僅 IEEE 摘要與出版 metadata 已核對；未宣稱已閱讀全文。

[8] F. Fakhrai Rad, P. Oghazi, İ. Onur, and A. Kordestani, “Adoption of AI-Based Order Picking in Warehouse: Benefits, Challenges, and Critical Success Factors,” *Review of Managerial Science*, vol. 19, pp. 3495–3540, 2025. DOI: [10.1007/s11846-025-00858-1](https://doi.org/10.1007/s11846-025-00858-1). 全文開放取得／已檢視。

[9] W. El Kadmiri, A. Benghabrit, A. Nait Sidi Moh, and M. Moufaddal, “Towards Resilient and Sustainable Smart Warehousing: A Systematic Literature Review and Multi-Dimensional Cross-Functional Framework,” *Cleaner Logistics and Supply Chain*, vol. 19, art. 100340, 2026. DOI: [10.1016/j.clscn.2026.100340](https://doi.org/10.1016/j.clscn.2026.100340). 全文開放取得／已檢視。

[10] GS1, *GS1 Logistic Label Guideline*, Release 1.3, ratified July 2019. [Official guideline](https://ref.gs1.org/guidelines/logistic-label/1.3.0/). 官方標準全文已檢視。先前規劃文件曾暫記為 2023，依 PDF 版次頁修正為 2019。

[11] R. Michel, “2025 Warehouse/DC Operations Survey: Tech Adoption Marches On,” *Supply Chain Management Review*, Nov. 3, 2025. [Original survey article](https://www.scmr.com/article/2025-warehouse-dc-operations-survey-tech-adoption-marches-on/inventory-management). 產業調查，n=101；非同儕審查且不應外推至全球母體。

[12] E. Tabassi, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, National Institute of Standards and Technology, 2023. DOI: [10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1). 官方全文已檢視。

[13] M. M. Alam, R. Azizbek Nurkat Ugli, K. J. Tanha, and T. Jun, “AI-Enhanced Digital Twin Systems for Warehouse Logistics Optimization: A Review of Challenges with Solutions and Future Directions,” *ICT Express*, vol. 12, no. 2, pp. 459–479, 2026. DOI: [10.1016/j.icte.2026.01.009](https://doi.org/10.1016/j.icte.2026.01.009). 正式開放取用全文與出版 metadata 已核對。

---

## 待查證清單

1. [7] 的完整作者名單、全文、資料切分、異常標註方式、baseline、公平比較及 production deployment 細節。
2. 自製資料能否達到 300–500 張、至少三類文件與五種版型；取得授權與去識別程序尚未執行。
3. 各品項是否強制管理 batch／lot 或 expiry，以及效期警示天數；須由實際品項主檔與組織政策確認。
4. Agent 是否相較 B0/B1 提升 macro-F1、evidence coverage 或降低錯誤自動通過率；所有結果均待實驗。
5. 「本系統之整合方式具文獻新穎性」及「沒有完全相同系統」仍須完成更廣泛的系統性文獻檢索。
6. 目標學生電腦的 CPU、RAM、OS、單張處理時間及可接受成本尚待登錄與實測。

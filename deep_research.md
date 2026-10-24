# Deep Research：Smart Warehouse AI Agent

> 文件版本：v0.1｜更新日期：2026-10-24  
> 研究範圍：倉儲管理、資料品質、物流作業、文件 AI 與高風險 AI 決策。  
> 證據原則：優先引用正式論文、標準組織及政府框架；產業調查僅用於背景且標示樣本限制。無法取得全文者不推論全文內容。尚未執行的系統效果一律屬 **Expected Outcomes**。

## 0. 研究方法與證據界線

本文件以 `warehouse inventory accuracy`、`inventory record inaccuracy`、`RFID visibility`、`cycle counting`、`agentic document understanding`、`domain-specific information extraction`、`human oversight`、`AI traceability` 等關鍵詞，檢索出版社頁面、ACL Anthology、IEEE Xplore、NIST 與 GS1。來源依下列層級使用：

1. 同儕審查的實證研究或正式會議論文。
2. 系統性回顧及正式標準／政府風險框架。
3. 有清楚樣本與方法說明的產業調查，只用來描述情境，不作因果推論。

本文將零售店、distribution center 與 warehouse 研究並列，是因為三者皆處理 inventory record、identification 與 material flow；但其環境不完全相同，任何數值均不得直接外推至本專題的臺灣倉儲資料。

---

# Q1：五個核心思維模式

## M1. 流程與狀態守恆（Process and State Conservation）

### 定義

專家不把庫存視為一個孤立數字，而把它視為由收貨、驗收、上架、移庫、揀貨、出貨、退貨與盤點等事件所推導的狀態。每筆異動都應回答「哪一個品項、從何處、移至何處、數量多少、何時、依據哪份文件」。若期初量加合法流入減合法流出不等於期末量，問題可能來自實體作業、紀錄時間差、錯誤識別或未登錄事件，而不應立即被解讀為失竊或 OCR 錯誤。

### 實務案例

出庫單顯示 SKU-A 出庫 12 件，WMS on-hand 為 10 件。系統不應直接把數量改為 10，也不能僅顯示「負庫存」。它應查詢保留量、待入庫、最近移庫、單位換算及單據時間，確認 12「箱」是否被誤讀為 12「件」，或庫存快照是否早於該筆收貨事件。

### 可信證據

- Rad et al. 將 receiving 定義為卸貨、檢查品質與數量差異、更新庫存，而 picking 要求取得正確品項與數量，顯示倉儲資料與作業步驟不可分離 [DR8]。
- Destro et al. 以 system dynamics 分析 inventory record inaccuracy（IRI）對 picking productivity、lost sales 與 warehouse capacity utilization 的影響，並區分 ghost 與 hidden inventory [DR16]。
- El Kadmiri et al. 將智慧倉儲依 inbound、storage、outbound SKU flows 與不同決策層級整合，說明 KPI 必須放回流程位置解讀 [DR9]。

### 如何影響 AI Agent 系統設計

- 建立 `InventoryEvent` schema，而不只保存最終 `on_hand`。
- Rule Engine 應包含數量守恆、單位一致性、event-time 與 snapshot-time 規則。
- Planner 遇到負庫存前，先查詢必要事件與時間戳；資料不足則輸出 `TEMPORAL_DATA_MISSING`，而非臆測原因。
- Evidence bundle 必須同時引用單據行、庫存列與計算式。

## M2. 唯一識別與端到端追溯（Identity and Traceability）

### 定義

倉儲判斷的前提不是「名稱看起來相似」，而是實體、物流單元、品項、批號與交易文件能透過穩定識別碼連結。追溯性要求知道一項資料的來源、轉換及後續使用；識別碼缺漏或錯配時，系統應保持不確定，而不是以模糊比對自動覆寫。

### 實務案例

OCR 將 `SKU-0O18` 讀成 `SKU-0018`，字串相似度很高，但兩者可能是不同品項。若條碼解得 GTIN，且物流單元具有 SSCC，Agent 應優先使用可驗證識別；若只有模糊品名，僅能列候選並送人工確認。

### 可信證據

- GS1 Logistic Label Guideline 指出 master data alignment 是有效收發的前提，SSCC 應保存以支援追溯，未知品項難以有效收貨；規範亦涵蓋 GTIN、count、batch/lot 與日期等 Application Identifiers [DR10]。
- GS1 指南要求實際物流單元的 variable data 應與 Despatch Advice／ASN 相符，並建議保留 SSCC 關係 [DR10]。
- NIST GAI Profile 將 provenance 描述為追蹤資料來源與歷史的機制，並建議記錄來源、修改及 metadata [DR13]。

### 如何影響 AI Agent 系統設計

- 定義 identifier hierarchy：barcode/GTIN/SSCC exact match > verified master-data key > human-confirmed alias > fuzzy candidate。
- 模糊比對工具只能回傳 candidates、score 與 evidence，不得直接 mutate SKU。
- 每一結構化欄位保存 page、bbox、OCR span、decoder source 與 transformation history。
- 重複單據檢查使用組合鍵與版本政策，避免只比較單號字串。

## M3. 資料品質是「適合用途」而非單一準確率（Fitness for Use）

### 定義

資料是否可用取決於決策用途。對倉儲而言，accuracy、completeness、consistency、timeliness、uniqueness 與 validity 可能同時重要；一張 OCR 字元準確率高的單據，若缺少關鍵批號或快照過期，仍不適合自動放行。資料品質亦必須分層量測：字元、欄位、單據、跨來源一致性及決策結果不能混為一談。

### 實務案例

單據 99% 文字辨識正確，但唯一錯字落在數量 `10`→`100`。文件層平均 accuracy 看似良好，交易風險卻很高。另一情況是全部欄位皆正確，但庫存快照為昨日資料；此時問題是 timeliness 而非 OCR accuracy。

### 可信證據

- SROIE 將文字定位、OCR 與 KIE 分成不同任務，支持分層評估而非以單一 OCR 分數代表業務正確性 [DR4]。
- DocVQA 顯示單純組合文字辨識模組不必然達成整體文件理解，結構相關問題仍具挑戰 [DR5]。
- DeHoratius and Raman 對單一零售商 37 家店、近 370,000 筆紀錄的研究發現 IRI 具有品類與門市的系統性差異，且盤點作法等因素可減輕不準確；該數字不應外推至本專題，但證明帳實誤差不可一概視為隨機噪音 [DR14]。

### 如何影響 AI Agent 系統設計

- 分別維護 OCR confidence、field validity、cross-source consistency、snapshot freshness 與 decision confidence。
- 關鍵欄位採 risk-weighted threshold，不以文件平均信心掩蓋高風險欄位。
- 評估同時報 CER/WER、per-field F1、Exact Match、anomaly macro-F1、false auto-accept 與 evidence coverage。
- 資料過期、缺欄與衝突設為不同 reason codes，避免單一「低信心」無法診斷。

## M4. 例外導向與風險分級（Exception-oriented, Risk-based Control）

### 定義

專業作業不追求讓 AI 自動處理所有案件，而是將可重複、低風險、證據完整的案件快速通過，把人的注意力集中在高損失、低信心、規則衝突或新型態例外。自動化權限應隨風險降低，而不是隨模型自信無限制增加。

### 實務案例

數量欄信心 0.93 對一般耗材可能足以提出低風險通過建議；對高價或受效期管制品項，即使同樣信心仍需覆核。若 Rule Engine 同時命中未知 SKU 與負庫存，應提升 severity，凍結 recommendation，要求人工確認原始影像及主檔。

### 可信證據

- NIST AI RMF 要求明確區分 human-AI roles，並依情境定義 human oversight；可信任特性包含 valid/reliable、accountable/transparent、explainable/interpretable [DR12]。
- NIST GAI Profile 強調 provenance、測試、驗證及風險管理，而非只以平均效能作安全依據 [DR13]。
- Rad et al. 的實務研究指出 AI-based picking 雖可改善距離與時間，仍有組織與實施挑戰限制充分利用，支持人、流程與技術共同設計 [DR8]。

### 如何影響 AI Agent 系統設計

- Decision Policy 採 `severity × confidence × evidence coverage × data freshness`。
- 高風險、來源矛盾、規則衝突及未見類型一律 `HUMAN_REVIEW_REQUIRED`。
- 主要安全指標包括 false auto-accept rate、appropriate escalation rate 與 human correction rate。
- 原型只具 recommendation authority，沒有正式 WMS/ERP write tool。

## M5. 閉環校正與根因學習（Closed-loop Reconciliation and Root-cause Learning）

### 定義

盤點發現差異只是偵測，不是完成改善。專家會保留「差異如何產生、在哪個流程首次出現、如何修正、是否再發」的資料，使 control、audit 與流程改善形成閉環。AI Agent 的錯誤亦應被分類與回饋，而不是只覆寫正確答案。

### 實務案例

盤點發現 SKU-B 少 5 件。人工修正帳面數量後，若未追查收貨漏掃、錯誤上架、單位換算或揀貨未過帳，同樣差異仍會發生。系統應把 reviewer 的修正連結到 rule hit、流程節點及 error taxonomy，供後續調整規則與抽樣盤點優先順序。

### 可信證據

- Destro et al. 研究 cycle counting 與 IRI 對 distribution center performance 的互動，說明盤點資源與績效需共同考慮 [DR16]。
- Hardgrave, Aloysius, and Goyal 的兩個 field experiments 顯示 RFID visibility 對 IRI 的效果依品類而異，從無顯著改善至較大幅改善，意味工具效果受流程情境調節 [DR15]。
- Rao et al. 指出即使採 RFID，低 read-rate 仍會形成「invisible inventory」，並以 laboratory 與 field data 建立 tag performance 判準 [DR17]。

### 如何影響 AI Agent 系統設計

- Human review 必須記錄 approve/edit/reject、原因碼、時間與更正值。
- Audit log 採 append-only；更正新增版本，不覆寫原始 OCR 或初始建議。
- Dashboard 除顯示異常量，也按供應商、版型、流程節點與 error cause 分層。
- 後續規則或 prompt 更新以 frozen replay set 回歸測試，避免修正一類錯誤卻破壞另一類。

---

# Q2：三個最重要的專業爭論

## D1. 高度自動化決策 ↔ Human-in-the-loop

### 觀點 A：提高自動化可降低延遲與重複人工

Agentic document systems 顯示，task decomposition、tool use、validator 與 reviewer 可改善複雜文件處理；AID-Agent 在工業技術文件案例整合 OCR、LLM 與 domain tools [DR2]，DocAgent 則以動態讀取與 reviewer cross-check 處理長文件 [DR1]。倉儲 AI picking 案例也報告距離與時間改善 [DR8]。支持者因而主張，證據充分的重複案件應自動處理，以減少人工 bottleneck。

### 觀點 B：決策權應保留人工，尤其是高風險與不確定案件

NIST AI RMF 要求人機角色、監督及責任明確，並強調風險管理需貫穿生命週期 [DR12]。文件模型的高平均效能不能保證特定高價、效期或批號欄位無錯；AI picking 研究也指出 adoption challenges 可能阻礙系統效益 [DR8]。支持者主張，缺證據或高損失案件不應因模型「自信」而自動通過。

### Evidence

- 支持 A：[DR1], [DR2], [DR8] 顯示工具化 AI 在特定文件或倉儲任務的效率／效能潛力。
- 支持 B：[DR12], [DR13] 要求 contextual risk、provenance 與 human oversight；其論點是治理與安全，不是反對所有自動化。

### Current Consensus

可確認的共識不是「全自動」或「全人工」，而是依情境風險配置 automation level：低風險、schema-valid、證據完整且在已知分布內的案件可自動產生建議；高風險、低信心、衝突或 out-of-distribution 案件應交由人員。最終責任、override 與 auditability 必須清楚。

### Unresolved Problems

- 何種 false auto-accept rate 才可接受，會隨品項價值、法規與企業風險胃納改變，現階段**待查證**。
- 人工覆核可能出現 automation bias、疲勞與橡皮圖章效應；本專題尚未進行人因實驗。
- 過度升級會使 Agent 失去效率，過少升級則增加安全風險；最佳 threshold 需以 validation set 與成本矩陣決定。

## D2. Deterministic Rules ↔ Learning-based／LLM Agent

### 觀點 A：規則可解釋、可測試，適合硬性業務約束

重複單號、數量必須為正、JSON schema、SSCC/GTIN 格式及出庫不得造成政策禁止的負庫存等條件，可以 deterministic rules 表達。GS1 提供明確識別及資料交換要求 [DR10]；固定規則也容易建立 normal、boundary 與 error tests，適合高風險 control。

### 觀點 B：學習式模型與 Agent 能處理版型變異與非結構化上下文

SROIE 與 DocVQA 顯示文字、版面與語意需聯合理解 [DR4], [DR5]；AID-Agent 與 DocAgent 進一步用 tools 與 planning 處理複雜表格、跨頁或長文件 [DR1], [DR2]。純規則若遇到新供應商、同義欄名或不規則表格，維護成本可能快速增加。

### Evidence

- 支持 A：GS1 [DR10] 提供穩定語意及格式；Principe et al. 將 rule-based、LLM 與人工比較，明示 accuracy、scalability、cost-efficiency 存在權衡 [DR3]。
- 支持 B：AID-Agent 的 44 份工業文件案例與 DocAgent 的兩個長文件 benchmarks 支持工具化、情境化方法 [DR1], [DR2]。

### Current Consensus

對本專題較可靠的共識是 hybrid design：模型負責 perception、欄位候選、版面與非結構化語意；規則負責 schema、識別碼格式、數量約束、權限與 stop conditions；Agent 負責決定查什麼及何時升級。不能由 LLM 自行發明 domain policy，也不應要求規則處理所有視覺變異。

### Unresolved Problems

- hybrid system 的錯誤歸因較複雜：OCR、parser、rule 或 planner 都可能是 root cause。
- LLM 在繁體中文、中英混排與本地倉儲表單的 domain shift 尚無本專題實證。
- 規則覆蓋率與維護成本、模型成本與準確度之 crossover point 必須實測，不能由文獻直接給定。

## D3. 即時感測／RFID visibility ↔ 盤點與單據對帳

### 觀點 A：即時識別與 visibility 能降低帳實誤差

RFID 能較頻繁取得物品讀取事件，減少僅靠人工 barcode scan 的盲區。Hardgrave et al. 的兩個 field experiments 報告 RFID visibility 可降低 IRI，但效果依品類而異 [DR15]；另有實地研究比較 RFID 與 barcode inventory counts，結論偏向 RFID counts 較可靠 [DR18]。

### 觀點 B：感測技術不是 ground truth，仍需盤點、對帳與流程控制

RFID tag 可能漏讀、遮蔽或在特定環境表現不穩；Rao et al. 稱此為 invisible inventory conundrum [DR17]。DeHoratius and Raman 顯示 IRI 與流程複雜度、distribution structure、audit practices 等因素相關 [DR14]；cycle counting 研究則顯示盤點資源與作業績效需權衡 [DR16]。因此更多感測資料不自動等於正確庫存。

### Evidence

- 支持 A：[DR15], [DR18] 為 field evidence，但主要來自零售情境。
- 支持 B：[DR14], [DR16], [DR17] 顯示 IRI 有流程成因，且 RFID 本身也有 read-performance failure。

### Current Consensus

目前較合理的共識是多重控制：RFID／barcode 提供 transaction visibility；文件與 ASN 提供交易語意；WMS 保存系統狀態；cycle count 或 physical verification 提供獨立校正。任何單一來源都不應被無條件視為真值。Agent 應比較來源、時間戳與可靠度，而不是固定偏好某種技術。

### Unresolved Problems

- RFID 的成本效益與讀取率高度依品類、材質、設施與流程而異，不能以零售 field study 直接推估本專題場域。
- 發生來源衝突時，如何估計 source reliability 與決定盤點優先序，仍需本地資料。
- 本專題 MVP 以文件與庫存快照為主；RFID adapter 僅屬未來擴充，是否納入正式實驗為**待查證**。

---

# Q3：十個深度理解問題

## U1 — Why：為何高 OCR accuracy 不等於正確倉儲決策？

- **問題：** 若整份文件 CER 很低，為何仍不能自動過帳？
- **專業分析：** 平均 CER 對所有字元等權，但倉儲風險集中於 SKU、數量、單位、批號與效期。單一關鍵字元錯誤即可使交易語意完全改變；而庫存快照過期或主檔缺失甚至不是 OCR 能偵測的問題。
- **可能答案：** OCR accuracy 是 perception metric，不是 transaction correctness。必須再通過 schema、field-level、cross-source、domain-rule 與 risk checks。
- **證據依據：** SROIE 分開評估 OCR 與 KIE [DR4]；DocVQA 指出結構理解不能化約為文字辨識 [DR5]。
- **設計啟示：** 禁止用單一 mean OCR confidence 決定 auto-pass；採 critical-field minimum 與 evidence coverage。

## U2 — What-if：若單據與庫存快照都正確，但時間基準不同呢？

- **問題：** 10:00 的單據與 09:55 的 snapshot 顯示矛盾，是真異常嗎？
- **專業分析：** 可能只是 event-time 與 processing-time 不一致。未檢查 snapshot timestamp 就觸發負庫存，會產生誤報。
- **可能答案：** 先查詢資料 freshness、未過帳事件與時區；若無法取得同步狀態，判定 `TEMPORAL_UNCERTAINTY` 並升級，而非判定 inventory error。
- **證據依據：** 智慧倉儲框架強調跨 physical/cyber layers 與 SKU flow phases 的整合 [DR9]；IRI dynamics 在盤點間持續變動 [DR19]。
- **設計啟示：** 所有 inventory rows 強制包含 `as_of_time`；Planner 在 reconcile 前執行 freshness check。

## U3 — Trade-off：提高自動通過率與降低危險錯放，何者優先？

- **問題：** confidence threshold 應設多高？
- **專業分析：** threshold 不是純技術常數，而是 false accept 與 false escalation 的成本權衡。高價、管制或易腐品的 false accept 成本較高；低價耗材可能容許較高 automation coverage。
- **可能答案：** 以品項風險分層，繪製 coverage–risk curve，依 validation set 與成本矩陣選 threshold；高風險保持人工 gate。
- **證據依據：** NIST 要求依 context of use 管理風險與 human oversight [DR12], [DR13]。
- **設計啟示：** Policy 不採全域單一 threshold；報 false auto-accept rate 及 appropriate escalation rate。

## U4 — Failure Case：若 OCR、barcode 與主檔給出三個不同 SKU，誰是正確的？

- **問題：** Agent 能否自行選最高信心來源？
- **專業分析：** 各來源的 confidence 尺度不可直接比較；barcode 也可能貼錯或解碼錯，主檔可能過期。沒有獨立驗證時，不存在保證正確的單一來源。
- **可能答案：** 比較 identifier hierarchy、來源時間、校驗碼、SSCC/ASN 關係及人工影像；若仍衝突，輸出 candidates 與 `IDENTITY_CONFLICT`。
- **證據依據：** GS1 強調 master data alignment、正確標籤與實物／ASN 一致 [DR10]；RFID 研究顯示感測也可能有 invisible inventory [DR17]。
- **設計啟示：** 不允許 silent overwrite；衝突必須保留全部 evidence IDs。

## U5 — Evidence：什麼才算足以支持一項異常建議的證據？

- **問題：** 一段自然語言解釋是否足夠？
- **專業分析：** 解釋可以流暢但不真實。可稽核證據需能定位來源並重算：原始影像區域、OCR span、欄位轉換、庫存 row、規則版本及計算式。
- **可能答案：** 每個 material claim 至少連結一個可驗證 evidence object；涉及跨來源比較時，需同時引用兩側來源。
- **證據依據：** NIST GAI Profile 強調 provenance metadata 與來源歷史 [DR13]；DocAgent 使用 reviewer 交叉檢查互補來源 [DR1]。
- **設計啟示：** 定義 `EvidenceRef` schema 與 evidence coverage；unsupported claim 阻擋 decision。

## U6 — Comparison：為何必須保留 OCR + Rules baseline？

- **問題：** 既然 Agent 較新，是否只需與純 OCR 比較？
- **專業分析：** 若 Agent 與純 OCR 的差異同時包含 parser、rules、database query 與 model，無法知道增益來自哪一部分。B1 是重要控制組，能測量 deterministic domain logic 已能解決多少問題。
- **可能答案：** B0、B1、B2 共用 OCR、schema、split 與硬體；B2 只增加 planning、adaptive tool use、evidence gate 與 escalation。
- **證據依據：** Principe et al. 直接比較 human、rule-based 與 LLM IE，指出多面向 trade-off [DR3]；AID-Agent 亦與 conventional extractors 比較 [DR2]。
- **設計啟示：** 建立共同 benchmark runner，另做 remove-rule、remove-query、remove-evidence-gate ablations。

## U7 — Design Decision：為何 Planner 要用有限狀態機，而非開放式 autonomous loop？

- **問題：** 限制步數是否會犧牲 Agent 能力？
- **專業分析：** 開放迴圈可能重複調用工具、放大成本或執行未授權操作；倉儲決策流程有限且可枚舉。有限狀態仍可根據缺資料動態分支，同時便於測試與稽核。
- **可能答案：** MVP 採 state machine、tool allowlist、maximum steps、retry-once 與 explicit stop；未來只有在 failure analysis 證明不足時才擴張自主性。
- **證據依據：** AID-Agent 支持中央工具排程與 validator [DR2]；NIST 強調角色、責任與風險控制 [DR12]。
- **設計啟示：** 對每個 state 建合法轉移測試；越權或 timeout 一律 fail-safe。

## U8 — Real-world Scenario：人工核准後才發現錯誤，責任與資料如何處理？

- **問題：** 是否直接修改舊 log，使資料看起來正確？
- **專業分析：** 覆寫會破壞 auditability，也無法區分 AI 建議與人工決定。真實系統需要 correction event、操作者、理由與時間。
- **可能答案：** 保留原始輸入、初始建議與人工核准，另新增 reversal/correction record；正式庫存仍由授權 WMS 流程處理。
- **證據依據：** NIST 的 accountability、transparency 與 lifecycle governance [DR12]；GS1 的追溯與資料關係保存 [DR10]。
- **設計啟示：** append-only log、versioned decisions、separation of duties；MVP 無 WMS write permission。

## U9 — What-if／Failure：新供應商版型造成大量低信心，應降低 threshold 嗎？

- **問題：** 為維持 throughput 而降低門檻是否合理？
- **專業分析：** 新版型是 distribution shift；降低門檻可能提高 silent error。短期應提高人工覆核並收集失敗樣本，長期再更新 parser 或模板。
- **可能答案：** 啟動 `UNSEEN_TEMPLATE` policy、隔離處理、抽樣雙人標註；只有 validation 顯示安全才調整 threshold。
- **證據依據：** SROIE 與 AID-Agent 都揭示版面及複雜表格是抽取難點 [DR2], [DR4]；NIST 要求 deployment 後持續 measure/manage [DR12]。
- **設計啟示：** template-held-out test、drift monitoring、版本回歸與 threshold change log。

## U10 — Why／Real-world Scenario：為何盤點差異不能直接標成單據錯誤？

- **問題：** 帳面 20、實盤 18，而最近一張單據為 2 件，能否判定單據重複？
- **專業分析：** 相同差額可能源自漏掃、錯放、損耗、單位錯誤、先後時間或重複交易。只靠數值相等屬 correlation，不是 causal evidence。
- **可能答案：** 將「差異」與「可能原因」分開；只有 document ID、event log、location 或獨立證據支持時，才提升特定 root-cause confidence。
- **證據依據：** DeHoratius and Raman 顯示 IRI 與多種 SKU／store factors 相關 [DR14]；後續研究亦指出 shrinkage、記錄與上架錯誤具有不同影響 [DR20]。
- **設計啟示：** anomaly label 與 root-cause hypothesis 分欄；輸出 calibrated confidence 與 alternative hypotheses。

---

# 4. Deep Research → 可執行系統知識

## 4.1 Domain Knowledge Rules

| Rule ID | 由研究轉換的規則 | Evidence | Agent action | 驗證 |
|---|---|---|---|---|
| DK-ID-01 | exact verified identifier 優先於 fuzzy text；候選不得自動覆寫 | M2, [DR10] | conflict → review | known aliases、near-match、wrong-label tests |
| DK-ID-02 | 同一 supplier + document type + document ID 重複時，先查歷史事件，不直接重複入帳 | M1/M2 | flag duplicate risk | duplicate/non-duplicate fixtures |
| DK-QTY-01 | quantity 必須為正且 unit 可正規化；表頭／明細應守恆 | M1, [DR8] | invalid → correction/review | boundary/unit conversion tests |
| DK-TIME-01 | snapshot 必須有 `as_of_time`；過期或晚於事件的狀態需明示 | M1/M3 | temporal uncertainty | time-zone/out-of-order tests |
| DK-STOCK-01 | 預估負庫存屬 high severity，但原因保持 unknown，除非另有證據 | M1/M5 | block recommendation | stock/event sequence fixtures |
| DK-BATCH-01 | batch/expiry 只對主檔標示受管理之 SKU 強制；門檻屬組織政策 | M2, [DR10] | missing → review | managed/unmanaged SKU tests |
| DK-EVID-01 | 每項 material claim 必須引用可解析 evidence ID | M2/M4 | unsupported → stop | broken/missing reference tests |
| DK-RISK-01 | high severity、low confidence、source conflict 或 insufficient coverage 必須人工覆核 | M4, [DR12] | human gate | decision-table coverage |
| DK-AUDIT-01 | 更正以新事件追加，不覆寫原始輸入／建議 | M5, [DR12] | append correction | trace replay/hash tests |
| DK-DRIFT-01 | unseen template 或顯著 confidence shift 不得以降低門檻直接維持 throughput | M3/M5 | quarantine/sample | held-out template tests |

> `expiry warning days`、高價品門檻、snapshot 最大允許年齡與 false auto-accept tolerance 均為組織情境參數，目前**待查證**，不得寫死為通用產業規則。

## 4.2 Agent Planning

Deep Research 將 Planner 轉為以下 evidence-driven 狀態，而非自由文字推理：

1. `VALIDATE_INPUT`：驗證格式、任務、文件雜湊與權限。
2. `EXTRACT_EVIDENCE`：執行 OCR／barcode，保留 bbox、頁碼與 confidence。
3. `NORMALIZE_AND_VALIDATE`：套 schema、identifier hierarchy、unit/date rules。
4. `CHECK_FRESHNESS`：檢查 document time、snapshot time 與未決事件。
5. `QUERY_CONTEXT`：只讀查詢 master data、inventory、document history。
6. `RECONCILE`：比對單據、ASN／識別碼、庫存與事件守恆。
7. `ASSESS_EVIDENCE`：計算 coverage，列出 conflict 與 unknown。
8. `DECIDE_OR_ESCALATE`：依 policy 輸出 recommendation 或 human gate。
9. `APPEND_TRACE`：保存版本、rule hits、證據及人工結果。

Planner 的分支原則是「缺什麼證據，才調用什麼工具」；超過 maximum steps、工具失敗或資料仍矛盾時停止並升級，不用生成內容填補空缺。

## 4.3 異常決策邏輯

建議決策函數：

```text
risk = severity(domain_rule_hits)
       × exposure(item_value_or_control_class)
       × uncertainty(field_confidence, source_conflict, freshness)

if unsupported_claim or missing_critical_field:
    disposition = REQUEST_CORRECTION_OR_REVIEW
elif high_severity or source_conflict or out_of_distribution:
    disposition = HUMAN_REVIEW_REQUIRED
elif evidence_coverage < policy.minimum_coverage:
    disposition = HUMAN_REVIEW_REQUIRED
else:
    disposition = RECOMMEND_PASS_OR_FLAG
```

此式是系統設計草案，不是已驗證的風險模型。`severity`、`exposure`、threshold 與權重須由 validation data、教師／domain reviewer 及實際政策共同決定，現階段均為**待查證**。

## 4.4 可驗證研究假設

- H1：加入欄位 schema 與 deterministic rules 的 B1，其 field validity 與已知異常 precision 將優於 B0；**Expected Outcome，待實驗**。
- H2：加入 adaptive query、freshness check 與 evidence gate 的 B2，對跨來源異常的 recall 與 evidence coverage 將優於 B1；**Expected Outcome，待實驗**。
- H3：risk-based human gate 將降低 false auto-accept，但提高 escalation rate 與 latency；**Expected Outcome，待實驗**。
- H4：unseen-template 與 degraded-image 條件將使三方案效能下降，B2 是否更具韌性不預設答案。

---

# References

[DR1] L. Sun et al., “DocAgent: An Agentic Framework for Multi-Modal Long-Context Document Understanding,” *EMNLP 2025*, 2025. DOI: [10.18653/v1/2025.emnlp-main.893](https://doi.org/10.18653/v1/2025.emnlp-main.893).

[DR2] B. Li, J. Conen, and F. Aller, “AID-Agent: An LLM-Agent for Advanced Extraction and Integration of Documents,” *REALM 2025*, pp. 80–88, 2025. [ACL Anthology](https://aclanthology.org/2025.realm-1.6/).

[DR3] R. A. Principe, M. Viviani, and N. Chiarini, “Enhancing Information Extraction with Large Language Models: A Comparison with Human Annotation and Rule-Based Methods in a Real Estate Case Study,” *LDK 2025*, pp. 243–254, 2025. [ACL Anthology](https://aclanthology.org/2025.ldk-1.25/).

[DR4] Z. Huang et al., “ICDAR2019 Competition on Scanned Receipt OCR and Information Extraction,” *ICDAR 2019*, pp. 1516–1520. DOI: [10.1109/ICDAR.2019.00244](https://doi.org/10.1109/ICDAR.2019.00244).

[DR5] M. Mathew, D. Karatzas, and C. V. Jawahar, “DocVQA: A Dataset for VQA on Document Images,” *WACV 2021*, pp. 2200–2209. DOI: [10.1109/WACV48630.2021.00225](https://doi.org/10.1109/WACV48630.2021.00225).

[DR6] A. Puga Mendoza, J. L. Caballero Chávez, and R. Torres Mendoza, “Applications and Methodologies of Internet of Things in Warehouses and Inventory Management: A Systematic Literature Review,” *Procedia Computer Science*, vol. 253, pp. 1236–1245, 2025. DOI: [10.1016/j.procs.2025.01.185](https://doi.org/10.1016/j.procs.2025.01.185).

[DR7] 作者名單**待查證**, “Research on Abnormal Inventory Detection Algorithm in Warehouse Management System,” *ICAIEM 2025*. DOI: [10.1109/ICAIEM66060.2025.11139221](https://doi.org/10.1109/ICAIEM66060.2025.11139221). 僅摘要與 metadata 已核對。

[DR8] F. Fakhrai Rad, P. Oghazi, İ. Onur, and A. Kordestani, “Adoption of AI-Based Order Picking in Warehouse: Benefits, Challenges, and Critical Success Factors,” *Review of Managerial Science*, vol. 19, pp. 3495–3540, 2025. DOI: [10.1007/s11846-025-00858-1](https://doi.org/10.1007/s11846-025-00858-1).

[DR9] W. El Kadmiri, A. Benghabrit, A. Nait Sidi Moh, and M. Moufaddal, “Towards Resilient and Sustainable Smart Warehousing: A Systematic Literature Review and Multi-Dimensional Cross-Functional Framework,” *Cleaner Logistics and Supply Chain*, vol. 19, art. 100340, 2026. DOI: [10.1016/j.clscn.2026.100340](https://doi.org/10.1016/j.clscn.2026.100340).

[DR10] GS1, *GS1 Logistic Label Guideline*, Release 1.3, 2019. [Official guideline](https://ref.gs1.org/guidelines/logistic-label/1.3.0/).

[DR11] R. Michel, “2025 Warehouse/DC Operations Survey: Tech Adoption Marches On,” *Supply Chain Management Review*, 2025. [Original article](https://www.scmr.com/article/2025-warehouse-dc-operations-survey-tech-adoption-marches-on/inventory-management). 產業調查，n=101，非同儕審查。

[DR12] E. Tabassi, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, 2023. DOI: [10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1).

[DR13] NIST, *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*, NIST AI 600-1, 2024. [Official PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).

[DR14] N. DeHoratius and A. Raman, “Inventory Record Inaccuracy: An Empirical Analysis,” *Management Science*, vol. 54, no. 4, pp. 627–641, 2008. DOI: [10.1287/mnsc.1070.0789](https://doi.org/10.1287/mnsc.1070.0789).

[DR15] B. C. Hardgrave, J. A. Aloysius, and S. Goyal, “RFID-Enabled Visibility and Retail Inventory Record Inaccuracy: Experiments in the Field,” *Production and Operations Management*, vol. 22, no. 4, pp. 843–856, 2013. DOI: [10.1111/poms.12010](https://doi.org/10.1111/poms.12010).

[DR16] I. R. Destro, F. H. Staudt, K. Somensi, and C. Taboada, “The Impacts of Inventory Record Inaccuracy and Cycle Counting on Distribution Center Performance,” *Production*, vol. 33, e20220077, 2023. DOI: [10.1590/0103-6513.20220077](https://doi.org/10.1590/0103-6513.20220077).

[DR17] S. Rao et al., “On the ‘Invisible Inventory Conundrum’ in RFID-Equipped Supply Chains: A Data Science Approach to Assessing Tag Performance,” *Journal of Business Logistics*, 2019. DOI: [10.1111/jbl.12232](https://doi.org/10.1111/jbl.12232). 作者完整名單須於最終格式化 References 前再次核對，現標為**待查證**。

[DR18] M. Bertolini, E. Bottani, G. Romagnoli, and G. Vignali, “The Impact of RFID Technologies on Inventory Accuracy in the Apparel Retailing: Evidence from the Field,” *RFID Technology and Applications*, vol. 6, no. 4, 2015. DOI: [10.3233/RFT-150069](https://doi.org/10.3233/RFT-150069).

[DR19] J. Barratt, T. Kull, and A. Sodero, “Inventory Record Inaccuracy Dynamics and the Role of Employees within Multi-Channel Distribution Center Inventory Systems,” *Journal of Operations Management*, vol. 63, pp. 6–24, 2018. DOI: [10.1016/j.jom.2018.09.003](https://doi.org/10.1016/j.jom.2018.09.003). 作者名字與順序應由出版頁於最終 References 再次核對，現標為**待查證**。

[DR20] M. A. Waller et al., “Inventory Record Inaccuracy: Causes and Labor Effects,” *Journal of Operations Management*, vols. 39–40, pp. 63–78, 2015. DOI: [10.1016/j.jom.2015.07.006](https://doi.org/10.1016/j.jom.2015.07.006). 作者完整名單應由出版頁於最終 References 再次核對，現標為**待查證**。

## 待查證項目總表

1. DR7、DR17、DR19、DR20 的完整作者 metadata 與可取得全文範圍。
2. 本地倉儲對 batch、expiry、高價品、snapshot freshness 及負庫存的實際政策。
3. 自製資料規模、類別分布、標註一致性與授權。
4. Human review 的可接受 workload、automation bias 與 reviewer agreement。
5. RFID 是否納入 MVP；目前只作爭論與未來工具擴充的證據。
6. 所有 H1–H4、threshold 與效能目標均待實驗驗證。

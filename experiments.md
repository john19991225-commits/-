# Smart Warehouse AI Agent — Experimental Design

> 版本：v0.1｜日期：2026-10-24  
> 狀態：**Experimental Protocol / Not Run**。本文件只定義方法與空白結果表，不包含任何虛構觀測值。

## 1. Research Questions and Primary Comparison

本實驗比較相同單據與相同庫存情境下，人工流程、固定規則 pipeline 與 Domain AI Agent 的準確度、安全性、時間及人工負擔。

- RQ-E1：三種方案在文字／欄位正確性上是否不同？
- RQ-E2：三種方案對倉儲異常與重複單據的偵測能力是否不同？
- RQ-E3：Agent 是否能以較低人工介入完成任務，同時不提高危險錯放？
- RQ-E4：Agent 的工具選擇是否符合 gold workflow，並能在失敗情境安全完成或升級？

Primary endpoint 預定為「異常偵測 macro-F1」。正式執行前須由指導教師確認並 freeze；目前狀態為**需要人工確認**。

## 2. Baselines

### B0 — 人工輸入與人工核對

- 操作者查看原始單據，手動輸入 document number、date、warehouse、pallet type、SKU、quantity、unit。
- 操作者以相同 read-only 測試資料庫／查詢畫面核對歷史單據與庫存。
- 操作者自行標記異常並給出 disposition。
- 計時包含閱讀、輸入、查詢、核對與送出。
- 不允許看到 B1/B2 輸出。至少兩名操作者的可行性與研究倫理／同意程序須先由教師確認。

### B1 — OCR + Fixed Rules

- 使用與 B2 完全相同的 OCR engine、版本、影像前處理、parser、SQLite snapshot 與 rule version。
- 按固定順序執行 `OCR → parse → query → duplicate check → rules → output`。
- 不根據中間結果重新規劃工具；只能依預先寫死的 error handling 停止。
- 不使用 LLM，不產生 adaptive query，不因缺資料選擇額外工具。

### B2 — OCR + Domain AI Agent

- 與 B1 共用 OCR、parser、database、rules、thresholds 及測試資料。
- Agent 理解 RECEIPT／ISSUE／CHECK 任務，在 allowlist 中選擇 history、inventory、analytics 及 domain tools。
- Agent 可根據缺資料、來源衝突與 tool error 重新規劃一次或升級人工；有 step limit、stop condition 與 audit trace。
- 最終 decision gate 仍為確定性 policy；LLM（若啟用）不得自行改寫硬性倉儲規則。

## 3. Fairness Controls

| Control | Requirement |
|---|---|
| Test documents | B0、B1、B2 使用完全相同、順序經控制的 test manifest |
| Ground truth | 同一 adjudicated gold labels；evaluators 不得依某 baseline 輸出修改 gold |
| Inventory state | 每一 test case 由相同 immutable SQLite snapshot 還原 |
| OCR | B1 與 B2 使用相同 engine/config；不得只替 B2 手動修 OCR |
| Parser/rules | B1 與 B2 使用相同 schema、normalization、rule version 與 thresholds |
| Hardware | B1、B2 在同一電腦、相同 background policy 執行；記錄 CPU/RAM/OS |
| Human timing | B0 計時包含完整工作；B2 人工覆核時間納入 end-to-end time |
| Leakage | 同一原始單據、其增強版及相同 template/vendor 不得跨 split |
| Failed cases | 不排除 failure；依事前 failure taxonomy 記錄，除非符合 frozen exclusion rule |

## 4. Dataset and Split

### 4.1 Planned Dataset

1. Public pretest：SROIE／DocVQA 僅用於 OCR/KIE pipeline sanity check，不用作臺灣倉儲效能結論。
2. Main dataset：目標 300–500 張匿名或合成中英倉儲單據，至少 3 種 document types、5 種 templates。
3. Paired operational data：每張文件配對 immutable inventory snapshot、master data、document history 與 expected decision。
4. Anomaly labels：duplicate、missing critical field、unknown SKU、invalid quantity/unit、insufficient stock、warehouse mismatch、batch/expiry missing（若政策適用）、normal。

實際樣本數、來源、授權及類別分布尚未完成，均為**Not Run／待查證**。

### 4.2 Split Protocol

- 以 `vendor_id + template_id` 作 group split，預定 train/validation/test = 60/20/20。
- `random_seed = 20261024`；正式建立 manifest 後 freeze checksum。
- train：開發 parser 或 prompt；validation：選 threshold、政策與 retry；test：只執行一次主要分析。
- 依 document type 與 anomaly class 檢查分層平衡；若 group constraint 無法同時分層，優先防 leakage，並完整報告不平衡。
- 同一 test manifest 複製給三種 baseline；B0 以 randomized/counterbalanced order 降低疲勞與學習順序影響。
- Test 前不得查看 label；若修正程式，原 test run 保留並將後續執行標為 secondary analysis。

## 5. Metrics and Calculation

### 5.1 字元辨識準確率

以 Levenshtein distance 計算 Character Error Rate：

```text
CER = (Substitutions + Deletions + Insertions) / Number of gold characters
Character Accuracy = max(0, 1 - CER)
```

- 正規化規則須事前固定：Unicode normalization、換行／空白與全半形處理。
- B1/B2 報相同 OCR output 的 accuracy，用來確認輸入一致。
- B0 可另報 `Manual Transcription Character Accuracy`；表格中不得將它誤稱為 OCR accuracy。
- 同時報 corpus-level CER 與 document-level mean/median；空白 gold 文件不納入 CER，原因需記錄。

### 5.2 重要欄位 Exact Match Accuracy

```text
Field EM = Number of exactly correct field values / Number of evaluated field values
Document EM = Documents where all required fields are correct / Total documents
```

重要欄位：document number、date、warehouse、pallet type、SKU、quantity、unit。日期、Decimal、unit 可先依 frozen normalization 比較；不得使用人工主觀「接近正確」。除 micro average 外，逐欄報 EM，避免簡單欄位掩蓋 quantity/SKU 錯誤。

### 5.3 異常偵測 Precision、Recall、F1-score

每種 anomaly class 採 one-vs-rest：

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 × Precision × Recall / (Precision + Recall)
```

- 分母為 0 時記為 `undefined`，不任意填 0；macro-F1 計算規則在 test 前 freeze。
- 報 per-class、macro 與 micro 結果及 confusion matrix。
- 同一文件可有多個異常，故採 multi-label evaluation。
- `root-cause hypothesis` 與 `anomaly detected` 分開評估，不能以猜中差異量視為找出原因。

### 5.4 重複單據偵測準確率

```text
Duplicate Accuracy = (TP_duplicate + TN_duplicate) / All test cases
```

另報 duplicate Precision、Recall、F1 與 confusion matrix，避免 class imbalance 使 accuracy 虛高。Confirmed duplicate 與 fuzzy candidate 分開；只有 gold-confirmed duplicate 算 positive。

### 5.5 每張單據平均處理時間

```text
Mean Time = Sum(end timestamp - start timestamp) / Number of completed attempts
```

- 另報 median、P95、standard deviation 與 failed-case time。
- B0：從文件顯示至人工送出；B1：從 input accepted 至 result persisted；B2：包含 Agent tools、等待與實際人工覆核。
- 系統 warm-up 可另列，不得只刪除慢案例；是否排除首次 model load 須事前規定。

### 5.6 人工介入比例

```text
Human Intervention Rate = Cases requiring any human correction/review / All cases
```

- B0 依定義為 100%，但仍需量測介入時間與錯誤率。
- B1 若 failure 或規則要求人工，計入介入。
- B2 的 `HUMAN_REVIEW_REQUIRED`、補件或人工 edit 均計入；只觀看結果但不要求動作者不計入，定義須事前一致。
- 同時報 appropriate escalation、unnecessary escalation、missed escalation。

### 5.7 Agent 工具選擇與任務完成率

僅 B2 適用工具選擇；B0/B1 記為 N/A。

```text
Tool Selection Precision = Correct selected tool calls / All selected tool calls
Tool Selection Recall    = Required tool calls executed / All gold-required tool calls
Safe Tool Rate           = Allowed, schema-valid calls / All tool calls
Task Completion Rate     = Cases satisfying all completion criteria / All assigned cases
```

每個 case 需先建立 gold workflow：required、optional、forbidden tools。任務完成需同時符合：（1）輸出 schema valid；（2）必要查詢已完成；（3）disposition 正確或適當升級；（4）沒有 forbidden write；（5）material claims 有 evidence。單純輸出文字不算完成。

## 6. Experimental Procedure

1. 完成 data card、annotation guide、雙人標註及 adjudication。
2. 產生 group split manifest，固定 seed、checksum 與 anomaly distribution。
3. 在 validation set 選定 OCR config、normalization、rules、decision thresholds 與 maximum steps。
4. Freeze code commit、environment、model/OCR/rule/prompt versions；目前尚無 Git repository，此項**未完成**。
5. 建立每個 test case 的 clean database snapshot 與 gold workflow。
6. B0 操作者接受相同簡短訓練；以 counterbalanced order 完成人工流程。
7. B1/B2 在相同硬體執行；每 case 還原相同 snapshot，捕捉 wall-clock、tool trace、RAM、failure。
8. 禁止三種 baseline 互看輸出；由 evaluator 對 frozen gold 自動計分。
9. 匯出 raw predictions、confusion matrices、bootstrap 95% CI 與 error taxonomy。
10. Primary analysis 完成後才做 ablation、threshold sensitivity、degraded-image 與 unseen-template secondary experiments。

## 7. Statistical Comparison

- Accuracy／EM／task completion 等 paired binary outcome：報 paired difference 與 bootstrap 95% CI；若做假設檢定，可採 McNemar test。
- 每張時間為 paired continuous outcome：先報 median/IQR；可用 paired bootstrap 或 Wilcoxon signed-rank test。
- F1：以 document-level paired bootstrap 重抽樣，保持同一文件在三方案中的配對。
- 多重比較：primary comparison 預定 B2 vs B1；B0 為 operational reference。若執行多個 confirmatory tests，需事前決定 Holm correction。
- 除統計顯著性外，報 absolute difference、CI、錯誤案例與實務代價。
- 若樣本不足，不做過度因果宣稱；將結果標為 pilot feasibility。

## 8. Empty Result Tables — Not Run

### 8.1 Primary Results

| Metric | B0 Manual | B1 OCR + Fixed Rules | B2 OCR + Domain AI Agent | B2 − B1 | 95% CI | Status |
|---|---:|---:|---:|---:|---:|---|
| Character Accuracy | — | — | — | — | — | Not Run |
| Important-field EM | — | — | — | — | — | Not Run |
| Document EM | — | — | — | — | — | Not Run |
| Anomaly macro-Precision | — | — | — | — | — | Not Run |
| Anomaly macro-Recall | — | — | — | — | — | Not Run |
| Anomaly macro-F1 | — | — | — | — | — | Not Run |
| Duplicate Accuracy | — | — | — | — | — | Not Run |
| Mean time/document | — | — | — | — | — | Not Run |
| Median time/document | — | — | — | — | — | Not Run |
| Human intervention rate | — | — | — | — | — | Not Run |
| Task completion rate | — | — | — | — | — | Not Run |

### 8.2 Agent-only Results

| Metric | B2 Result | 95% CI | Status |
|---|---:|---:|---|
| Tool Selection Precision | — | — | Not Run |
| Tool Selection Recall | — | — | Not Run |
| Safe Tool Rate | — | — | Not Run |
| Evidence Coverage | — | — | Not Run |
| Appropriate Escalation Rate | — | — | Not Run |
| False Auto-accept Rate | — | — | Not Run |

### 8.3 Per-anomaly Results

| Anomaly | Support | B0 F1 | B1 F1 | B2 F1 | Status |
|---|---:|---:|---:|---:|---|
| Duplicate document | — | — | — | — | Not Run |
| Missing critical field | — | — | — | — | Not Run |
| Unknown SKU | — | — | — | — | Not Run |
| Invalid quantity/unit | — | — | — | — | Not Run |
| Insufficient stock | — | — | — | — | Not Run |
| Warehouse mismatch | — | — | — | — | Not Run |
| Batch/expiry missing | — | — | — | — | Not Run / policy pending |

## 9. Quality Gates Before Running

- [ ] 指導教師確認 primary endpoint、split ratio、sample target 與 statistical plan。
- [ ] Domain reviewer 確認 anomaly definitions、severity 與 gold workflow。
- [ ] Data owner 確認授權、去識別、retention 與可公開範圍。
- [ ] Train/validation/test manifest 與 checksum freeze。
- [ ] B0 人員、訓練方式、倫理／同意與 counterbalancing 確認。
- [ ] B1/B2 共用 OCR、parser、rules、thresholds 的 automated assertion。
- [ ] 評估 script 以小型 fixture 驗證，但不查看 test labels。
- [ ] 結果表仍為空白，直到正式執行並保存 raw artifacts。


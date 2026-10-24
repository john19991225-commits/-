# Smart Warehouse AI Agent — Processing Flowchart

> 流程涵蓋 Input → Processing → OCR → Validation → Analytics → Domain Knowledge → Decision → Output，並包含辨識失敗、缺欄、重複、庫存不一致、人工確認與重新處理。

```mermaid
flowchart TD
    START([Start]) --> IN["Input<br/>Query + Image or PDF + Data Source"]
    IN --> VFILE{"File and task valid?"}
    VFILE -->|No| EINPUT["Exception: INPUT_REJECTED<br/>return correction request"]
    EINPUT --> END1([End])
    VFILE -->|Yes| PROC["Processing<br/>hash, trace ID, page rendering, preprocessing"]
    PROC --> OCR["OCR<br/>text, bbox, confidence"]
    OCR --> OOK{"OCR usable?"}
    OOK -->|No, first attempt| RETRY["Adjust preprocessing<br/>rotate, crop, denoise"]
    RETRY --> OCR
    OOK -->|No, retry exhausted| OFAIL["Exception: OCR_FAILED"]
    OFAIL --> HUMAN["Human confirmation<br/>replace file, enter correction, reject"]
    OOK -->|Yes| PARSE["Parse fields to schema"]
    PARSE --> VALID["Validation<br/>types, required fields, identifiers, units"]
    VALID --> MISS{"Critical fields missing?"}
    MISS -->|Yes| HUMAN
    MISS -->|No| ACQ["Retrieve inventory, master data, document history"]
    ACQ --> DSOK{"Data source available and fresh?"}
    DSOK -->|No| DFAIL["Exception: source unavailable or stale"]
    DFAIL --> HUMAN
    DSOK -->|Yes| ANALYTICS["Analytics<br/>normalize, duplicate check, reconcile, statistics"]
    ANALYTICS --> DUP{"Duplicate document?"}
    DUP -->|Confirmed exact duplicate| DUPFLAG["High-risk duplicate flag"]
    DUP -->|Candidate only| DUPREVIEW["Record candidate and uncertainty"]
    DUP -->|No| STOCK{"Inventory consistent?"}
    DUPREVIEW --> STOCK
    STOCK -->|No| INVFLAG["Inventory mismatch finding<br/>preserve alternative causes"]
    STOCK -->|Yes| DOMAIN["Domain Knowledge<br/>versioned warehouse rules"]
    INVFLAG --> DOMAIN
    DUPFLAG --> DOMAIN
    DOMAIN --> RULEERR{"Rule conflict or policy missing?"}
    RULEERR -->|Yes| HUMAN
    RULEERR -->|No| CONF["Assess confidence, evidence coverage, severity, freshness"]
    CONF --> DECIDE{"Decision gate"}
    DECIDE -->|Low risk and sufficient evidence| RECOMMEND["Recommend pass or low-risk flag"]
    DECIDE -->|High risk, conflict, low confidence| HUMAN
    HUMAN --> HACTION{"Human action"}
    HACTION -->|Approve or edit| FINAL["Output<br/>fields, anomaly, recommendation, evidence"]
    HACTION -->|Reject| REJECT["Output rejected with reason"]
    HACTION -->|Reprocess with new evidence| LOOP["Append attempt and correction"]
    LOOP --> PROC
    RECOMMEND --> FINAL
    FINAL --> LOG["Append-only operation log"]
    REJECT --> LOG
    LOG --> END2([End])
```

## 決策與迴圈說明

| 節點 | 條件 | 動作 | 是否可重試 |
|---|---|---|---|
| File and task valid | 格式、大小、權限、scenario | 不合法即拒絕 | 使用者可重新上傳 |
| OCR usable | 關鍵區域可讀且 confidence 達政策門檻 | 第一次失敗可改變影像前處理 | 自動最多一次 |
| Critical fields missing | SKU、數量、document ID 等依 scenario 判定 | 轉人工補值或換檔 | 人工可要求 reprocess |
| Data source available and fresh | SQLite/Sheets 可讀、`as_of_time` 可接受 | 不可用或過期即停止自動判斷 | 資料恢復後可重跑 |
| Duplicate document | exact composite key 或僅 fuzzy candidate | Exact 標高風險；candidate 保持不確定 | 人工確認後可繼續 |
| Inventory consistent | 單位、時間與事件考量後仍有差異 | 建立 mismatch finding，不直接指定原因 | 補充事件後可重跑 |
| Rule conflict | 規則互斥、版本缺失、政策未定 | 轉人工／設定錯誤 | 修正規則版本後重跑 |
| Decision gate | severity、confidence、coverage、freshness | 低風險建議或 human gate | 人工可 approve/edit/reject/reprocess |

## Exception 原則

- 工具 error 與「查無資料」是不同狀態；連線失敗不得偽裝成空集合。
- 自動 retry 只允許一次且必須改變前處理參數，避免無限迴圈。
- 人工 reprocess 沿用 `trace_id`，增加 `attempt_no`，保留之前結果。
- 所有 End path 均留下 audit event；log 失敗時整體狀態不得標示完成。


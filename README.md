# Smart Warehouse AI Agent — MVP

可執行的學生級 Domain AI Agent 原型：接收單據、擷取文字、解析倉儲欄位、查詢 SQLite、檢查重複與庫存規則、輸出證據，並只在使用者確認後寫入測試資料庫。

## 專題背景與目標

本專題全名為 **Smart Warehouse AI Agent — 智慧倉儲單據辨識與庫存異常決策代理人**。研究問題不是只把文件轉成文字，而是探討如何結合 OCR、庫存資料、確定性倉儲規則、有限工具規劃、異常判斷、證據追溯與人工確認，形成可在一般學生電腦開發的 Domain AI Agent。正式實驗尚未執行；目前成果是 Proposal、Target Design、Experimental Protocol 與匿名合成資料 MVP。

> 安全界線：只使用匿名／合成資料。請勿把真實敏感單據、`.env`、API key 或本機資料庫提交至版本控制。此 MVP 不連接正式 WMS/ERP。

## 已實作的端到端流程

```text
任務 + 圖片/PDF
  → bounded Agent plan
  → configurable OCR adapter
  → document schema parser
  → SQLite inventory/history lookup
  → duplicate + inventory analytics
  → deterministic warehouse rules
  → result + anomaly + evidence
  → explicit human confirmation
  → test database write + append-only audit
```

目前 `RuleBasedPlanner` 會判斷 RECEIPT／ISSUE／CHECK intent，並以 allowlist 與最大長度限制工具計畫；但三種 intent 目前大多仍走相同七步流程，尚未完成依中間結果動態補查或 replan。因此，本版本應稱為 **bounded orchestration MVP**，不是完整自主 Agent。OCR、SQL、Decimal 計算、重複鍵和倉儲規則本身都是確定性工具，不宣稱為 LLM reasoning。

## Project Structure

```text
app.py                      Streamlit UI 與人工確認
agent/                      planner、orchestration、models、LLM config boundary
ocr/                        OCR provider interface、PDF/Tesseract/test adapters、parser
analytics/                  重複與庫存分析
domain/                     版本化規則的 MVP 實作
database/                   SQLite schema、seed、query、write、audit
tests/                      unittest 端到端與失敗測試
data/                       匿名合成 fixture；本機 DB 不進 Git
scripts/init_db.py          合成資料庫初始化
architecture.md             系統架構
flowchart.md                流程與例外
algorithm.md                Algorithm 1
DESIGN.md                   設計與實作映射
```

## Requirements

- Python 3.11
- Streamlit、Pandas、Pillow、pypdf
- 圖片 OCR 選配：Tesseract executable + `pytesseract`
- 掃描型 PDF 尚需 PDF-to-image renderer，目前未實作

安裝 Python 套件：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Tesseract 是獨立系統程式，不會因安裝 `pytesseract` 自動出現。請依作業系統安裝，並確認 `tesseract --version` 可執行。

## Configuration

複製 `.env.example` 為 `.env`，不要提交 `.env`：

```powershell
Copy-Item .env.example .env
```

主要設定：

| Variable | Values | 狀態 |
|---|---|---|
| `DATABASE_PATH` | SQLite path | 已實作／已測試 |
| `OCR_PROVIDER` | `auto`, `embedded_pdf`, `tesseract`, `synthetic` | adapter 已實作；環境支援見下方 |
| `OCR_LANGUAGE` | Tesseract language code | 未在目前環境驗證 |
| `LLM_PROVIDER` | `disabled` 或未來 provider | `disabled` 已測；外部 adapter 未實作 |
| `LLM_API_KEY` | secret | 不得硬編碼；目前不使用 |

`synthetic` 只能處理 UTF-8 測試 fixture，不得在正式 UI 中偽裝為影像 OCR。

## Run

初始化匿名測試資料庫：

```powershell
python -m scripts.init_db
```

啟動 UI：

```powershell
python -m streamlit run app.py
```

預設 `OCR_PROVIDER=auto`：文字型 PDF 使用 pypdf 擷取 embedded text；圖片使用 Tesseract。若 Tesseract 未安裝，系統會回傳明確 OCR failure，不會產生假結果。

## Test

```powershell
python -m compileall -q agent ocr analytics domain database tests scripts app.py
python -m unittest discover -s tests -v
```

2026-10-24 實際執行結果：6 tests passed。涵蓋：

- 成功解析、查詢、規則檢查，確認前不寫入，確認後寫入並產生 audit。
- 第二次相同單號被偵測，SQLite unique constraint 阻擋重複寫入。
- 缺少單號、日期、倉別與品項時要求修正。
- 空白檔案安全失敗。
- 出庫量大於可用量時要求人工覆核。
- 圖片 OCR provider 不可用時回傳明確失敗，而非空白成功。

## Supported Fields

目前 parser 支援中英欄名：

- `DOCUMENT_NO`／`單據編號`
- `DATE`／`日期`
- `WAREHOUSE`／`倉別`
- `PALLET_TYPE`／`棧板型式`
- `ITEM`／`品項`，格式為 `SKU | description | quantity | unit`

測試 fixture 見 [data/synthetic_receipt.txt](data/synthetic_receipt.txt)。

## 成功、失敗與尚未實作

### 已實作且已測試

- 合成 OCR 端到端路徑。
- 欄位解析、SQLite seed/query/history/write/audit。
- 重複單號、缺欄、數量、單位、SKU、棧板型式與出庫可用量規則。
- Agent intent 與 bounded tool plan。
- 證據 IDs、人工確認、重複寫入保護。

### 已實作但目前環境未完成外部驗證

- Streamlit UI：已通過 import/smoke check；尚未由真人完成瀏覽器互動測試。
- Embedded-text PDF provider：程式路徑已實作；尚未加入合成 PDF automated test。
- Tesseract image provider：程式路徑已實作；目前機器沒有 Tesseract/pytesseract，故只驗證 fail-safe。

### 尚未實作

- 掃描型 PDF page rendering 與逐頁 image OCR。
- Google Sheets adapter。
- 外部或本地 LLM provider；目前使用 bounded rule-based planner。
- OCR bounding boxes（embedded PDF/test provider 只有文字 evidence；Tesseract MVP 亦未取 word-level boxes）。
- 批號、效期、GTIN/SSCC、單位換算表與 fuzzy duplicate production policy。
- 正式登入權限、加密、PII redaction、production-grade immutable log。
- 真實使用者、人因、效能、CER/F1 與安全門檻實驗。

## Known Limitations

- Parser 是明確格式的 MVP regex，不代表能泛化至任意供應商版型。
- `PASS_RECOMMENDED` 只表示未命中目前已知規則，不是正式交易核准。
- 測試結果使用匿名合成資料，不能外推為真實倉儲效能。
- 此目錄目前不是 Git repository；`.gitignore` 已準備，但尚無 Git history 可稽核。

## Proposal 與實驗文件

| 文件 | 用途 | 目前狀態 |
|---|---|---|
| [`proposal.md`](proposal.md) | Abstract、Introduction、Related Work、Deep Research | 文件草稿已完成；文獻中標示的待查證項目仍須人工複核 |
| [`deep_research.md`](deep_research.md) | 5 Mindsets、3 Controversies、10 Questions | 已完成文件整理 |
| [`architecture.md`](architecture.md) | 可編輯 Mermaid 系統架構 | 已完成 |
| [`flowchart.md`](flowchart.md) | 可編輯 Mermaid 流程圖 | 已完成 |
| [`algorithm.md`](algorithm.md) | 具行號的 Algorithm 1 | 已完成 |
| [`experiments.md`](experiments.md) | 三組 baseline、公平比較、指標公式與空白結果表 | **Experimental Protocol / Not Run** |
| [`proposal_slides.md`](proposal_slides.md) | 18 頁 Proposal 簡報原始內容與逐頁講稿 | Markdown 已完成；PPTX 尚未匯出 |
| [`proposal_checklist.md`](proposal_checklist.md) | 依課程權重進行提交前品質檢查 | 已更新，仍有人工確認與未完成項目 |

實驗尚未執行，因此 `experiments.md` 的 Observed Results 保持空白，不得以設計目標、MVP 單元測試或 Expected Outcomes 代替正式比較結果。三組 baseline 必須共用凍結後的 test set、gold labels、inventory snapshot 與計時規則。

目前環境沒有直接產生或人工檢視 PowerPoint 的工具；`proposal_slides.md` 保留了可轉換的 18 頁內容，可後續用 Marp、Pandoc 或人工貼入 PowerPoint，再由報告者檢查中文字型、Mermaid 圖與版面。

## GitHub 與目前進度

- Repository：<https://github.com/john19991225-commits/->
- 已完成：Proposal 五部分、Deep Research 5/3/10、Architecture、Flowchart、Algorithm、Experimental Protocol、18 頁簡報原稿、合成資料 MVP 與 automated tests。
- 部分完成：圖片 OCR provider、embedded-text PDF、bounded planner、SQLite audit。
- Planned：真實／授權資料集、掃描 PDF、動態 Agent planning、Google Sheets、LLM adapter、正式 B0/B1/B2 實驗、PPTX 匯出、CI 與環境 lock。
- Results：只有 automated test 結果；沒有正式 OCR、異常偵測或效率實驗結果。

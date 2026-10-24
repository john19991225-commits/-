# Synthetic Data Only

本目錄只允許匿名或合成資料。`synthetic_receipt.txt` 是供 automated test 與本機 demo 使用的 UTF-8 fixture，不代表真實公司、供應商或庫存。

執行 `python scripts/init_db.py` 會建立 `data/warehouse.db` 並加入三筆匿名庫存。資料庫檔已由 `.gitignore` 排除，避免誤提交後續本機資料。


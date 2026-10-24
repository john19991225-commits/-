from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from agent.service import SmartWarehouseAgent
from database.repository import WarehouseRepository
from ocr.providers import provider_from_env


DB_PATH = Path(os.getenv("DATABASE_PATH", "data/warehouse.db"))


@st.cache_resource
def build_services() -> tuple[WarehouseRepository, SmartWarehouseAgent]:
    repository = WarehouseRepository(DB_PATH)
    repository.initialize()
    repository.seed_synthetic_inventory()
    return repository, SmartWarehouseAgent(repository, provider_from_env())


st.set_page_config(page_title="Smart Warehouse AI Agent", layout="wide")
st.title("Smart Warehouse AI Agent — MVP")
st.caption("匿名／合成資料優先；分析不會自動寫入，必須由使用者確認。")

repository, agent = build_services()
query = st.text_input("任務", "檢查入庫單據、重複紀錄與庫存規則")
uploaded = st.file_uploader("上傳圖片或 PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded and st.button("開始分析", type="primary"):
    st.session_state["analysis"] = agent.analyze(query, uploaded.getvalue(), uploaded.name)

result = st.session_state.get("analysis")
if result:
    st.subheader("Agent 執行計畫")
    st.dataframe(pd.DataFrame([vars(step) for step in result.plan]), use_container_width=True)
    if result.error:
        st.error(f"處理失敗：{result.error}")
    else:
        st.metric("狀態", result.status)
        st.metric("最低證據信心", f"{result.confidence:.2f}")
        st.subheader("辨識結果")
        st.json(result.to_dict()["document"])
        st.subheader("異常與規則")
        if result.findings:
            st.dataframe(pd.DataFrame([vars(item) for item in result.findings]), use_container_width=True)
        else:
            st.success("未發現已定義的異常；這不等於正式核准。")
        st.subheader("可追溯證據")
        st.dataframe(pd.DataFrame([vars(item) for item in result.evidence]), use_container_width=True)
        actor = st.text_input("確認者代號")
        confirmed = st.checkbox("我已檢查原始文件、欄位、異常與證據，確認寫入測試資料庫")
        if st.button("確認並寫入測試資料庫", disabled=not confirmed):
            try:
                row_id = agent.confirm_and_write(result, actor)
                st.success(f"已寫入測試資料庫，document row id={row_id}")
            except Exception as exc:
                st.error(f"寫入已阻擋：{exc}")

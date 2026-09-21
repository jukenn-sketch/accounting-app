import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from db import init_db, add_expense, get_expenses, delete_expense

# 初始化資料庫
init_db()

st.set_page_config(page_title="個人記帳本", page_icon="💰", layout="centered")
st.title("💰朱清勇 個人記帳 App")

# 建立頁籤：分頁 1 記帳、分頁 2 歷史明細（手機版更乾淨）
tab1, tab2 = st.tabs(["📝 新增消費", "📊 歷史明細"])

# ----------------- 分頁 1：新增消費 -----------------
with tab1:
    with st.form("expense_form", clear_on_submit=True):
        st.subheader("📝 新增消費資訊")
        date = st.date_input("📅 日期", datetime.date.today())
        category = st.selectbox(
            "🏷️ 類別", 
            ["🍔 餐飲", "🚗 交通", "🎮 娛樂", "🛍️ 購物", "🏠 居住/水電", "🏥 醫療", "📦 其他"]
        )
        amount = st.number_input("💵 金額 (NT$)", min_value=1, step=1, value=100)
        description = st.text_input("💬 備註（選填）", placeholder="例如：午餐便當")
        
        submitted = st.form_submit_button("➕ 新增這筆帳務", use_container_width=True)
        
        if submitted:
            add_expense(date, category, amount, description)
            st.success(f"成功記錄！ [{category}] ${amount} 元")
            st.rerun()  # 重新整理以同步更新歷史頁籤

# ----------------- 分頁 2：歷史明細 -----------------
with tab2:
    st.subheader("📊 消費記錄與統計")
    
    # 撈取資料
    data = get_expenses()
    
    if not data:
        st.info("目前還沒有任何消費記錄，快去新增第一筆吧！")
    else:
        # 轉換成 Pandas DataFrame 方便計算與顯示
        df = pd.DataFrame(data, columns=["ID", "日期", "類別", "金額", "備註"])
        
        # 轉換日期格式以利月份篩選
        df["日期_dt"] = pd.to_datetime(df["日期"])
        df["年月"] = df["日期_dt"].dt.strftime("%Y-%m")
        
        # 取得所有出現過的月份並排序（最新的月份在最前面）
        available_months = sorted(df["年月"].unique(), reverse=True)
        
        # 建立月份篩選下拉選單
        selected_month = st.selectbox("🗓️ 選擇查詢月份：", available_months)
        
        # 根據選取的月份過濾資料
        filtered_df = df[df["年月"] == selected_month]
        
        # 1. 顯示該月總消費
        month_total = filtered_df["金額"].sum()
        st.metric(label=f"💰 {selected_month} 當月總支出", value=f"NT$ {month_total:,}")
        
        st.divider()
        
        # 2. 圓餅图分析（類別占比）
        st.write("🍕 **類別消費比例**")
        cat_chart_data = filtered_df.groupby("類別")["金額"].sum().reset_index()
        
        fig = px.pie(
            cat_chart_data, 
            values="金額", 
            names="類別", 
            hole=0.4,  # 環狀圖樣式
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # 調整邊距讓手機顯示更滿
        fig.update_layout(margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 3. 顯示消費列表
        st.write("📋 **消費列表**")
        st.dataframe(
            filtered_df[["日期", "類別", "金額", "備註"]], 
            use_container_width=True,
            hide_index=True
        )
        
        # 刪除功能區塊
        st.divider()
        with st.expander("🗑️ 刪除紀錄"):
            # 將紀錄轉成下拉選單的選項內容
            delete_options = {f"[{row['日期']}] {row['類別']} ${row['金額']} ({row['備註']})": row["ID"] for _, row in df.iterrows()}
            selected_option = st.selectbox("選擇要刪除的紀錄：", list(delete_options.keys()))
            
            if st.button("❌ 確定刪除", type="primary", use_container_width=True):
                target_id = delete_options[selected_option]
                delete_expense(target_id)
                st.warning("已刪除該筆紀錄！")
                st.rerun()
import streamlit as st
import pandas as pd
import plotly.express as px
from db import init_db, add_expense, get_expenses, delete_expense

# -----------------------------------------------------------------------------
# 1. 頁面基本配置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="個人雲端記帳本",
    page_icon="💰",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. 全域 CSS 樣式設定（將介面字體與按鈕放大）
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* 主標題 (st.title) 縮小 */
    h1 {
        font-size: 32px !important;
        padding-bottom: 10px;
    }
    
    /* 副標題 (st.header / st.subheader) 縮小 */
    h2, h3 {
        font-size: 24px !important;
    }
    
    /* 調整一般內文與段落字體大小 */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    
    /* 輸入框、日期選擇器、下拉選單標籤 */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label, .stDateInput > label {
        font-size: 20px !important;
        font-weight: bold;
    }
    
    /* 按鈕文字大小 */
    .stButton > button {
        font-size: 20px !important;
        padding: 8px 20px;
    }
    
    /* 指標數據 (st.metric) */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 初始化資料庫（Supabase 介面相容）
# -----------------------------------------------------------------------------
init_db()

st.title("💰 個人雲端記帳本 (Supabase 版)")

# -----------------------------------------------------------------------------
# 4. 新增帳目區塊（側邊欄或主要區塊）
# -----------------------------------------------------------------------------
st.header("📝 新增消費紀錄")

col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

with col1:
    date = st.date_input("日期")

with col2:
    category = st.selectbox(
        "分類",
        ["餐飲", "交通", "娛樂", "日常用品", "醫療", "居住", "其他"]
    )

with col3:
    amount = st.number_input("金額", min_value=0.0, step=10.0, format="%.0f")

with col4:
    description = st.text_input("備註/說明", placeholder="例：晚餐、公車費")

if st.button("➕ 新增帳目", use_container_width=True):
    if amount > 0:
        add_expense(str(date), category, amount, description)
        st.success("✅ 帳目新增成功！")
        st.rerun()
    else:
        st.warning("⚠️ 請輸入大於 0 的金額")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 資料讀取與圖表分析區塊
# -----------------------------------------------------------------------------
expenses = get_expenses()

if expenses:
    # 轉為 Pandas DataFrame
    df = pd.DataFrame(expenses)
    
    # 自動給予/對齊欄位名稱
    if isinstance(expenses, list) and len(expenses) > 0:
        if isinstance(expenses[0], dict):
            df.columns = [str(col).lower() for col in df.columns]
        elif isinstance(expenses[0], (list, tuple)):
            if len(df.columns) == 5:
                df.columns = ['id', 'date', 'category', 'amount', 'description']
            elif len(df.columns) == 4:
                df.columns = ['date', 'category', 'amount', 'description']

    # 確保 amount 與 date 格式正確
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    if 'date' in df.columns:
        # 轉換為 datetime 型態並擷取 YYYY-MM 月份字串
        df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date_dt'].dt.strftime('%Y-%m')
    else:
        st.error("⚠️ 資料表中缺少 'date' 欄位")
        st.stop()

    # -----------------------------------------------------------------------------
    # 💡 依月份篩選功能
    # -----------------------------------------------------------------------------
    # 取得所有存在的月份清單（降冪排序，最新月份在最前）
    available_months = sorted([m for m in df['month'].unique() if pd.notna(m)], reverse=True)
    
    col_filter, col_empty = st.columns([2, 3])
    with col_filter:
        selected_month = st.selectbox("📅 請選擇查詢月份：", available_months, key="month_filter")
    
    # 根據選擇的月份過濾 DataFrame
    filtered_df = df[df['month'] == selected_month].copy()

    # 計算當月總支出
    total_amount = filtered_df['amount'].sum()
    
    # 顯示總消費指標
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(label=f"📊 {selected_month} 總消費金額", value=f"${total_amount:,.0f}")
    with col_metric2:
        st.metric(label="🔢 當月筆數", value=f"{len(filtered_df)} 筆")
    
    st.markdown("---")
    
    # -----------------------------------------------------------------------------
    # 圖表與明細展示（使用過濾後的 filtered_df）
    # -----------------------------------------------------------------------------
    if not filtered_df.empty:
        col_chart, col_table = st.columns([1, 1])
        
        with col_chart:
            st.subheader("📈 分類支出圓餅圖")
            fig = px.pie(
                filtered_df, 
                values='amount', 
                names='category', 
                title=f'{selected_month} 消費分類佔比',
                hole=0.4
            )
            fig.update_layout(
                font=dict(size=18),
                title_font_size=24
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_table:
            st.subheader("📋 詳細消費明細")
            display_cols = [c for c in ['date', 'category', 'amount', 'description'] if c in filtered_df.columns]
            
            styled_df = filtered_df[display_cols].style.set_properties(**{
                'font-size': '18px',
                'text-align': 'center'
            })
            
            st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info(f"💡 {selected_month} 尚無消費紀錄。")
        
    st.markdown("---")
       
    
    
    # -----------------------------------------------------------------------------
    # 6. 刪除紀錄區塊
    # -----------------------------------------------------------------------------
    st.subheader("🗑️ 刪除紀錄")
    
    df['delete_label'] = df.apply(
        lambda row: f"ID: {row.get('id', '')} | {row.get('date', '')} | {row.get('category', '')} | ${row.get('amount', 0):.0f} ({row.get('description', '')})", 
        axis=1
    )
    
    # 💡 加上 key="delete_selectbox" 避免 ID 重複衝突
    selected_to_delete = st.selectbox(
        "選擇要刪除的紀錄：", 
        df['delete_label'],
        key="delete_selectbox"
    )
    
    # 💡 加上 key="delete_button"
    if st.button("❌ 確認刪除選取紀錄", key="delete_button"):
        target_id = int(selected_to_delete.split("|")[0].replace("ID:", "").strip())
        delete_expense(target_id)
        st.success(f"已成功刪除紀錄 (ID: {target_id})！")
        st.rerun()
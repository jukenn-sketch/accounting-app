import streamlit as st
from supabase import create_client, Client

# 從 Secrets 讀取並清除前後空白/換行
url = str(st.secrets.get("SUPABASE_URL", "")).strip()
key = str(st.secrets.get("SUPABASE_KEY", "")).strip()

# 顯示除錯資訊（確認 secrets 讀取到的內容長度與格式）
st.write(f"🔍 URL: `{url}`")
st.write(f"🔍 Key 長度: {len(key)}")
if len(key) > 10:
    st.write(f"🔍 Key 開頭與結尾: `{key[:10]}...{key[-10:]}`")

# 初始化 Supabase
supabase: Client = create_client(url, key)

def fetch_data():
    try:
        response = supabase.table("expenses").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"讀取資料庫失敗：{e}")
        return []

def add_data(date, category, amount, description):
    try:
        data = {
            "date": str(date),
            "category": category,
            "amount": amount,
            "description": description
        }
        response = supabase.table("expenses").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"新增資料失敗：{e}")
        return None
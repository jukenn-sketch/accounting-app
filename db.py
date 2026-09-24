import streamlit as st
from supabase import create_client, Client

# 從 Secrets 讀取並自動清除前後空白與隱形字元
url = str(st.secrets.get("SUPABASE_URL", "")).strip()
key = str(st.secrets.get("SUPABASE_KEY", "")).strip()

# 初始化 Supabase 客戶端
supabase: Client = create_client(url, key)

def init_db():
    """Supabase 不需要像 SQLite 一樣初始化本地資料庫，保留空函式避免 app.py 報錯"""
    pass

def get_expenses():
    """對應 app.py 的讀取資料庫功能"""
    try:
        response = supabase.table("expenses").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"讀取資料庫失敗：{e}")
        return []

def add_expense(date, category, amount, description):
    """對應 app.py 的新增消費記錄功能"""
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
        st.error(f"新增帳目失敗：{e}")
        return None

def delete_expense(expense_id):
    """對應 app.py 的刪除消費記錄功能"""
    try:
        response = supabase.table("expenses").delete().eq("id", expense_id).execute()
        return response
    except Exception as e:
        st.error(f"刪除帳目失敗：{e}")
        return None
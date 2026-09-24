import streamlit as st
from supabase import create_client, Client

# 從 st.secrets 取得連線資訊
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(URL, KEY)

def init_db():
    pass # Supabase 免建檔，表格已在線上建立

def add_expense(date, category, amount, description):
    data = {
        "date": str(date),
        "category": str(category),
        "amount": float(amount),
        "description": str(description)
    }
    supabase.table("expenses").insert(data).execute()

def get_expenses():
    try:
        # 改用 "*" 撈取所有欄位，安全且不會遭遇 APIError
        response = supabase.table("expenses").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"讀取資料庫失敗：{e}")
        return []

def delete_expense(expense_id):
    supabase.table("expenses").delete().eq("id", expense_id).execute()
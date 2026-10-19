import streamlit as st
from supabase import create_client, Client

url = st.secrets.get("SUPABASE_URL", "NOT_FOUND")
key = st.secrets.get("SUPABASE_KEY", "NOT_FOUND")

# 直接在畫面上印出讀到的變數，看看是不是空字串
st.write(f"【除錯】讀到的 URL: `{url}`")
st.write(f"【除錯】讀到的 KEY 長度: `{len(key) if key != 'NOT_FOUND' else 0}`")

supabase: Client = create_client(url, key)

def init_db():
    pass

def get_expenses():
    try:
        response = supabase.table("expenses").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"讀取資料庫失敗：{e}")
        return []

def add_expense(date, category, amount, description):
    try:
        data = {
            "date": str(date),
            "category": category,
            "amount": int(amount),
            "description": description
        }
        response = supabase.table("expenses").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"新增帳目失敗：{e}")
        return None

def delete_expense(expense_id):
    try:
        response = supabase.table("expenses").delete().eq("id", expense_id).execute()
        return response
    except Exception as e:
        st.error(f"刪除帳目失敗：{e}")
        return None
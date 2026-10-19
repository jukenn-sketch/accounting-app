import streamlit as st
from supabase import create_client, Client

url = str(st.secrets.get("SUPABASE_URL", "")).strip()
key = str(st.secrets.get("SUPABASE_KEY", "")).strip()

# 初始化 Supabase 客戶端
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"初始化 Supabase 失敗：{e}")

def init_db():
    pass


def get_expenses():
    try:
        response = supabase.table("expenses").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        # 把真實的錯誤原因印出來，方便我們看出問題點
        st.warning(f"無法連線至雲端資料庫，詳細原因：{e}")
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
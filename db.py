import streamlit as st
from supabase import create_client, Client

# 從 Streamlit secrets 取得連線金鑰
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
#SUPABASE_URL = "https://cwpdrfbwaolcfqtraatm.supabase.co"
#SUPABASE_KEY = "https://cwpdrfbwaolcfqtraatm.supabase.co/rest/v1/"
supabase: Client = create_client(URL, KEY)

def init_db():
    # Supabase 已在線上建表，此處保留介面即可
    pass

def add_expense(date, category, amount, description):
    data = {
        "date": str(date),
        "category": category,
        "amount": int(amount),
        "description": description
    }
    supabase.table("expenses").insert(data).execute()

def get_expenses():
    response = supabase.table("expenses").select("id, date, category, amount, description").order("date", desc=True).order("id", desc=True).execute()
    # 轉成與之前 SQLite fetchall() 相同的 tuple 格式
    rows = [(item['id'], item['date'], item['category'], item['amount'], item['description']) for item in response.data]
    return rows

def delete_expense(expense_id):
    supabase.table("expenses").delete().eq("id", expense_id).execute()

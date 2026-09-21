
import sqlite3 

def init_db():
    # 連線至本地資料庫（若無檔案會自動建立）
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    # 建立記帳資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # 新增這段：將記帳資料寫入 SQLite 的函式
def add_expense(date, category, amount, description):
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, category, amount, description)
        VALUES (?, ?, ?, ?)
    ''', (str(date), category, amount, description))
    conn.commit()
    conn.close()

 # 取得所有帳務資料（按日期倒序排列，最新的在最上面）   
def get_expenses():
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC, id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

# 根據 ID 刪除特定一筆帳務
def delete_expense(expense_id):
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()


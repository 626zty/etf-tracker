import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    conn = sqlite3.connect('etf_holdings.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY,
                    fund_code TEXT,
                    report_date TEXT,
                    stock_code TEXT,
                    stock_name TEXT,
                    shares INTEGER,
                    weight REAL)''')
    conn.commit()
    conn.close()

def save_holdings(df):
    init_db()
    conn = sqlite3.connect('etf_holdings.db')
    df.to_sql('holdings', conn, if_exists='append', index=False)
    conn.close()

def get_latest_holdings(fund_code):
    conn = sqlite3.connect('etf_holdings.db')
    df = pd.read_sql(f"SELECT * FROM holdings WHERE fund_code='{fund_code}' ORDER BY report_date DESC LIMIT 1000", conn)
    conn.close()
    return df

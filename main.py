from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
from scraper import scrape_etf
from database import save_holdings, get_latest_holdings, init_db
from discord_bot import send_discord
import pandas as pd
from datetime import datetime
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

init_db()

async def daily_update():
    fund_codes = ["49YTW"]  # 在這裡新增其他 ETF，例如 "0050的fundCode"
    webhook = os.getenv("DISCORD_WEBHOOK")
    changes = []

    for code in fund_codes:
        try:
            df_new, date = await scrape_etf(code)
            save_holdings(df_new)
            
            # 簡單變化計算（與上次比較）
            prev = get_latest_holdings(code)
            if not prev.empty:
                # 這裡可以再優化比較邏輯
                changes.append(f"✅ {code} 已更新至 {date}，共 {len(df_new)} 檔持股")
        except Exception as e:
            changes.append(f"❌ {code} 更新失敗: {e}")

    if webhook and changes:
        send_discord(webhook, "\n".join(changes))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(daily_update())  # 啟動時先跑一次

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    df = get_latest_holdings("49YTW")
    if df.empty:
        return "<h1>尚無資料，請稍後再訪</h1>"
    
    latest_date = df['report_date'].max()
    latest = df[df['report_date'] == latest_date].sort_values('weight', ascending=False)
    
    html = f"<h1>00981A 持股 ({latest_date})</h1><table border='1'><tr><th>股票代號</th><th>名稱</th><th>股數</th><th>權重</th></tr>"
    for _, row in latest.head(30).iterrows():
        html += f"<tr><td>{row['stock_code']}</td><td>{row['stock_name']}</td><td>{row['shares']:,}</td><td>{row['weight']}%</td></tr>"
    html += "</table>"
    return html

# Railway 健康檢查
@app.get("/health")
def health():
    return {"status": "ok"}

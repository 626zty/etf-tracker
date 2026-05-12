import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re
from datetime import datetime

async def scrape_etf(fund_code: str):
    url = f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 取得資料日期
        try:
            date_text = await page.inner_text("text=資料日期:")
            date_match = re.search(r'資料日期[:：]\s*([\d/]+)', date_text)
            report_date = date_match.group(1) if date_match else datetime.now().strftime("%Y/%m/%d")
        except:
            report_date = datetime.now().strftime("%Y/%m/%d")
        
        holdings = []
        rows = await page.locator("table tr").all()
        for row in rows[1:]:
            cells = await row.locator("td").all_inner_texts()
            if len(cells) >= 4 and re.match(r'^\d+$', cells[0].strip()):
                holdings.append({
                    "fund_code": fund_code,
                    "report_date": report_date,
                    "stock_code": cells[0].strip(),
                    "stock_name": cells[1].strip(),
                    "shares": int(cells[2].replace(",", "")),
                    "weight": float(cells[3].replace("%", "").strip() or 0)
                })
        
        await browser.close()
        return pd.DataFrame(holdings), report_date

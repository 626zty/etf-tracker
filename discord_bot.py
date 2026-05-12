import requests
import os

def send_discord(webhook_url: str, message: str):
    if not webhook_url:
        return
    data = {
        "content": message,
        "embeds": [{"title": "📈 ETF 持股變化通知", "description": message, "color": 0x00ff00}]
    }
    try:
        requests.post(webhook_url, json=data, timeout=10)
    except:
        pass

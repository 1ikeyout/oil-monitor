import akshare as ak
import pandas as pd
import requests
import time
from datetime import datetime

# --- Configuration ---
# Replace with your actual credentials
TG_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# Tickers to monitor
TARGETS = [
    {"symbol": "油气开采及服务", "type": "sector", "name": "Oil & Gas Sector (881107)"},
    {"symbol": "159309", "type": "etf", "name": "Oil & Gas ETF (159309)"},
    {"symbol": "159588", "type": "etf", "name": "Petro & Gas ETF (159588)"}
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code != 200:
            print(f"Notification Error: {res.text}")
    except Exception as e:
        print(f"Connection Failed: {e}")

def get_market_data(target):
    try:
        if target['type'] == "sector":
            df = ak.stock_board_industry_hist_em(
                symbol=target['symbol'], 
                period="daily", 
                start_date="20250101", 
                adjust="qfq"
            )
        else:
            df = ak.fund_etf_hist_em(
                symbol=target['symbol'], 
                period="daily", 
                start_date="20250101", 
                adjust="qfq"
            )
        return df
    except Exception as e:
        print(f"Data Fetch Error ({target['symbol']}): {e}")
        return None

def execute_strategy():
    print(f"[{datetime.now()}] Scanning targets...")
    for item in TARGETS:
        df = get_market_data(item)
        if df is None or len(df) < 15:
            continue
            
        df = df.sort_values('日期' if '日期' in df.columns else 'date')
        val_col = '收盘' if '收盘' in df.columns else 'close'
        
        # Technical Indicators
        df['SMA3'] = df[val_col].rolling(window=3).mean()
        df['SMA5'] = df[val_col].rolling(window=5).mean()
        df['SMA10'] = df[val_col].rolling(window=10).mean()

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last[val_col]
        name = item['name']

        # Signal 1: 3/10 SMA Crossover
        if prev['SMA3'] <= prev['SMA10'] and last['SMA3'] > last['SMA10']:
            send_telegram(f"🚨 {name}: FAST BUY\n3/10 Golden Cross at {price}")
        elif prev['SMA3'] >= prev['SMA10'] and last['SMA3'] < last['SMA10']:
            send_telegram(f"🚨 {name}: FAST SELL\n3/10 Death Cross at {price}")
        
        # Signal 2: Price vs SMA5 Breakout
        elif prev[val_col] <= prev['SMA5'] and last[val_col] > last['SMA5']:
            send_telegram(f"📈 {name}: Breakout UP\nPrice crossed SMA5 at {price}")
        elif prev[val_col] >= prev['SMA5'] and last[val_col] < last['SMA5']:
            send_telegram(f"📉 {name}: Breakout DOWN\nPrice fell below SMA5 at {price}")

if __name__ == "__main__":
    send_telegram("Monitor Online: A-Share Oil & Gas Assets.")
    while True:
        execute_strategy()
        # Precise 15-minute interval
        time.sleep(900)

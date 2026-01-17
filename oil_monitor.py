import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

# Credentials from GitHub Secrets
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')

# Monitoring Targets
TARGETS = [
    {"symbol": "油气开采及服务", "type": "sector", "name": "Sector 881107"},
    {"symbol": "159309", "type": "etf", "name": "ETF 159309"},
    {"symbol": "159588", "type": "etf", "name": "ETF 159588"}
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

def run_analysis():
    print(f"Process started at: {datetime.now()}")
    for item in TARGETS:
        try:
            if item['type'] == "sector":
                df = ak.stock_board_industry_hist_em(symbol=item['symbol'], period="daily", start_date="20250101", adjust="qfq")
            else:
                df = ak.fund_etf_hist_em(symbol=item['symbol'], period="daily", start_date="20250101", adjust="qfq")
            
            if df is None or len(df) < 15: continue
            
            # Standardization
            date_col = '日期' if '日期' in df.columns else 'date'
            price_col = '收盘' if '收盘' in df.columns else 'close'
            df = df.sort_values(date_col)

            # Calculation: SMA
            df['SMA3'] = df[price_col].rolling(window=3).mean()
            df['SMA5'] = df[price_col].rolling(window=5).mean()
            df['SMA10'] = df[price_col].rolling(window=10).mean()

            last, prev = df.iloc[-1], df.iloc[-2]
            price, name = last[price_col], item['name']

            # Strategy Logic
            if prev['SMA3'] <= prev['SMA10'] and last['SMA3'] > last['SMA10']:
                send_telegram(f"🚨 {name}: BUY (3/10 Golden Cross) at {price}")
            elif prev['SMA3'] >= prev['SMA10'] and last['SMA3'] < last['SMA10']:
                send_telegram(f"🚨 {name}: SELL (3/10 Death Cross) at {price}")
            elif prev[price_col] <= prev['SMA5'] and last[price_col] > last['SMA5']:
                send_telegram(f"📈 {name}: Price Breakout UP (SMA5) at {price}")
            elif prev[price_col] >= prev['SMA5'] and last[price_col] < last['SMA5']:
                send_telegram(f"📉 {name}: Price Breakout DOWN (SMA5) at {price}")
        except Exception as e:
            print(f"Error on {item['name']}: {e}")

if __name__ == "__main__":
    run_analysis()

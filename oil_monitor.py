import akshare as ak
import pandas as pd
import requests
import os
import json
from datetime import datetime

# 1. Credentials from GitHub Secrets
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')

# 2. Monitoring Targets
TARGETS = [
    {"symbol": "油气开采及服务", "type": "sector", "name": "Sector_881107"},
    {"symbol": "159309", "type": "etf", "name": "ETF_159309"},
    {"symbol": "159588", "type": "etf", "name": "ETF_159588"}
]

def update_web_data(name, price, sma5):
    file_path = 'data.json'
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = {}
    except:
        all_data = {}

    if name not in all_data:
        all_data[name] = []

    # Record data for charts
    timestamp = datetime.now().strftime("%m-%d %H:%M")
    all_data[name].append({
        "time": timestamp, 
        "price": float(round(price, 4)), 
        "sma5": float(round(sma5, 4))
    })
    
    # Keep last 100 points
    all_data[name] = all_data[name][-100:]
    with open(file_path, 'w') as f:
        json.dump(all_data, f, indent=4)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"TG Error: {e}")

def run_analysis():
    print(f"Task Start: {datetime.now()}")
    for item in TARGETS:
        try:
            if item['type'] == "sector":
                df = ak.stock_board_industry_hist_em(symbol=item['symbol'], period="daily", start_date="20250101", adjust="qfq")
            else:
                df = ak.fund_etf_hist_em(symbol=item['symbol'], period="daily", start_date="20250101", adjust="qfq")
            
            if df is None or len(df) < 15: continue
            
            p_col = '收盘' if '收盘' in df.columns else 'close'
            df = df.sort_values('日期' if '日期' in df.columns else 'date')

            # SMA Calculation: $SMA_n = \frac{1}{n} \sum_{i=1}^{n} P_i$
            df['SMA3'] = df[p_col].rolling(window=3).mean()
            df['SMA5'] = df[p_col].rolling(window=5).mean()
            df['SMA10'] = df[p_col].rolling(window=10).mean()

            last, prev = df.iloc[-1], df.iloc[-2]
            curr_p, name = last[p_col], item['name']

            # Update JSON for Website
            update_web_data(name, curr_p, last['SMA5'])

            # Strategy Logic
            if prev['SMA3'] <= prev['SMA10'] and last['SMA3'] > last['SMA10']:
                send_telegram(f"🚨 {name}: BUY (3/10 Golden Cross) at {curr_p}")
            elif prev['SMA3'] >= prev['SMA10'] and last['SMA3'] < last['SMA10']:
                send_telegram(f"🚨 {name}: SELL (3/10 Death Cross) at {curr_p}")
            elif prev[p_col] <= prev['SMA5'] and last[p_col] > last['SMA5']:
                send_telegram(f"📈 {name}: Price Breakout UP (SMA5) at {curr_p}")
            elif prev[p_col] >= prev['SMA5'] and last[p_col] < last['SMA5']:
                send_telegram(f"📉 {name}: Price Breakout DOWN (SMA5) at {curr_p}")

        except Exception as e:
            print(f"Error on {item['name']}: {e}")

if __name__ == "__main__":
    run_analysis()

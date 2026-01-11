import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

# 从 GitHub Secrets 读取密钥
SEND_KEY = os.environ.get('MY_SEND_KEY')
SYMBOL = "CL" 

def send_wechat(title, content):
    if not SEND_KEY:
        print("Error: MY_SEND_KEY not set in Secrets")
        return
    url = f"https://sctapi.ftqq.com/{SEND_KEY.strip()}.send"
    data = {"title": title, "desp": content}
    try:
        res = requests.post(url, data=data, timeout=10)
        print(f"Push Result: {res.json()}")
    except Exception as e:
        print(f"Push Error: {e}")

def check_strategy():
    print(f"[{datetime.now()}] Fetching data...")
    try:
        df = ak.futures_foreign_hist(symbol=SYMBOL)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['SMA5'] = df['close'].rolling(window=5).mean()
        df['SMA20'] = df['close'].rolling(window=20).mean()

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        
        if prev_row['SMA5'] <= prev_row['SMA20'] and last_row['SMA5'] > last_row['SMA20']:
            send_wechat("Oil Alert: BUY", f"Golden Cross at ${last_row['close']}")
        elif prev_row['SMA5'] >= prev_row['SMA20'] and last_row['SMA5'] < last_row['SMA20']:
            send_wechat("Oil Alert: SELL", f"Death Cross at ${last_row['close']}")
        else:
            print(f"Price: {last_row['close']}. No signal.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
   check_strategy()
    if __name__ == "__main__":
    send_wechat("Cloud Test", "GitHub Action is working!")
    check_strategy()

